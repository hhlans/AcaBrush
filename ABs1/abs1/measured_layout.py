"""Measure and solve physical layout constraints without editing plot content.

SciPy is used only for the linear constraint solve. No plot is enlarged, label
rewritten, legend relocated or alignment constraint relaxed automatically.
"""
import string
import numpy as np
from matplotlib.transforms import Bbox
from .style import DEFAULT


class LayoutConflict(ValueError):
    """Requested physical layout constraints cannot be satisfied together."""


def finalize_measured_layout(fig, axes, *, rows, columns=None, plot_columns=(),
                             attachments=None, legend_panels=None,
                             horizontal_gap=.18, vertical_gap=.20, outer=.14,
                             gap_mode='minimum', max_horizontal_gap=None,
                             label_pad_pt=5, style=DEFAULT):
    """Arrange existing Axes in inches, preserving their data rectangles.

    rows: ordered sequences of panel names. Every panel must occur once.
    columns: optional name->logical starting column; None infers row order.
        Anchors only connect data panels in rows with the same data-panel
        count. Legend-only panels never create cross-row column anchors.
    plot_columns: explicit groups additionally requiring shared data-left edges.
        Conflicting content/data alignments raise LayoutConflict.
    attachments: name->sequence of attached Axes, e.g. an external colorbar.
        Their current offsets and dimensions are preserved, never stolen from
        the parent data rectangle. Use independently allocated colorbar Axes.
    legend_panels: name->Legend for legend-only axes; only the legend counts as
        occupied content, not its otherwise invisible container rectangle.
    gap_mode: 'fixed' gives exact gaps; 'minimum' finds the smallest equal gap
        per row compatible with ALL requested column constraints.
    max_horizontal_gap: optional upper bound; infeasibility is reported, never
        repaired by modifying typography, content or target plot dimensions.

    Returns a JSON-serializable geometry report. Repeated calls retain targets.
    A mosaic specifies relationships, not a fixed final canvas. Export without
    tight cropping. Call again after changing any text or legend arrangement.
    """
    try:
        from scipy.optimize import linprog
    except ImportError as exc:
        raise RuntimeError('Measured layout requires scipy.optimize.linprog') from exc
    axes=dict(axes);rows=[list(row) for row in rows]
    names=[name for row in rows for name in row]
    if not rows or any(not row for row in rows) or len(set(names))!=len(names) or set(names)!=set(axes):
        raise ValueError('rows must contain every supplied panel exactly once')
    if gap_mode not in ('fixed','minimum'):
        raise ValueError("gap_mode must be 'fixed' or 'minimum'")
    for value in (horizontal_gap,vertical_gap,outer,label_pad_pt):
        if not np.isfinite(value) or value<0:raise ValueError('Spacing must be finite and nonnegative')
    if max_horizontal_gap is not None and (not np.isfinite(max_horizontal_gap) or max_horizontal_gap<horizontal_gap):
        raise ValueError('max_horizontal_gap must be finite and at least horizontal_gap')
    plot_columns=[list(group) for group in plot_columns]
    attachments={} if attachments is None else attachments
    legend_panels={} if legend_panels is None else legend_panels
    row_counts=[sum(k not in legend_panels for k in row) for row in rows]
    panel_count={k:row_counts[r] for r,row in enumerate(rows) for k in row}
    columns=({k:c for row in rows for c,k in enumerate(k for k in row if k not in legend_panels)}
             if columns is None else dict(columns))
    if not set(columns)<=set(names):raise ValueError('Unknown panel in columns')
    # A logical column number is local to a row structure, never global across
    # rows with different numbers of data panels. Legends are not data panels.
    scoped_columns={}
    for k,col in columns.items():
        if k not in legend_panels:scoped_columns.setdefault((panel_count[k],col),[]).append(k)
    effective_columns=[g for g in scoped_columns.values() if len(g)>1]
    effective_plot_columns=[]
    for group in plot_columns:
        if any(k not in axes or k in legend_panels for k in group):
            raise ValueError('plot_columns must refer to data panels')
        for count in set(panel_count[k] for k in group):
            subset=[k for k in group if panel_count[k]==count]
            if len(subset)>1:effective_plot_columns.append(subset)
    numbered=[k for k in names if k not in legend_panels]
    if len(numbered)>26:raise ValueError('At most 26 numbered panels')
    for text in list(fig.texts):
        if text.get_gid()=='abs1-panel-label':text.remove()
    fig.canvas.draw();renderer=fig.canvas.get_renderer();dpi=fig.dpi
    targets={};margins={};widths={};heights={};offsets={}
    for k in names:
        ax=axes[k];box=ax.get_window_extent(renderer)
        if k in legend_panels:
            full=legend_panels[k].get_window_extent(renderer)
            widths[k]=full.width/dpi;heights[k]=full.height/dpi
            continue
        size=getattr(ax,'_abs_measured_target', (box.width/dpi,box.height/dpi))
        targets[k]=tuple(size)
        if min(size)<=0:raise ValueError('Data rectangles must have positive dimensions')
        boxes=[ax.get_tightbbox(renderer)];offsets[k]=[]
        for extra in attachments.get(k,()):
            eb=extra.get_window_extent(renderer)
            offsets[k].append((extra,[(eb.x0-box.x0)/dpi,(eb.y0-box.y0)/dpi,eb.width/dpi,eb.height/dpi]))
            boxes.append(extra.get_tightbbox(renderer))
        full=Bbox.union([b for b in boxes if b is not None])
        margins[k]=[max(0,(box.x0-full.x0)/dpi),max(0,(full.x1-box.x1)/dpi),
                    max(0,(box.y0-full.y0)/dpi),max(0,(full.y1-box.y1)/dpi)]
        l,r,b,t=margins[k];widths[k]=l+size[0]+r;heights[k]=b+size[1]+t
    # Unknowns: content-left per panel, equal horizontal gap per row, right edge.
    n=len(names);nr=len(rows);index={k:i for i,k in enumerate(names)};right=n+nr
    eq=[];beq=[];ub=[];bub=[]
    def equality(terms,value=0):
        a=np.zeros(right+1)
        for i,v in terms:a[i]+=v
        eq.append(a);beq.append(value)
    for r,row in enumerate(rows):
        for a,b in zip(row,row[1:]):
            equality([(index[b],1),(index[a],-1),(n+r,-1)],widths[a])
    for group in effective_columns:
        for k in group[1:]:equality([(index[k],1),(index[group[0]],-1)])
    for group in effective_plot_columns:
        for k in group[1:]:
            equality([(index[k],1),(index[group[0]],-1)],margins[group[0]][0]-margins[k][0])
    for k in names:
        a=np.zeros(right+1);a[index[k]]=1;a[right]=-1
        ub.append(a);bub.append(-widths[k]-outer)
    gap_upper=horizontal_gap if gap_mode=='fixed' else max_horizontal_gap
    bounds=[(outer,None)]*n+[(horizontal_gap,gap_upper)]*nr+[(0,None)]
    objective=np.zeros(right+1);objective[n:n+nr]=1
    result=linprog(objective,A_ub=np.array(ub),b_ub=np.array(bub),
        A_eq=np.array(eq) if eq else None,b_eq=np.array(beq) if eq else None,
        bounds=bounds,method='highs')
    if not result.success:
        raise LayoutConflict('Equal gutters, column anchors and optional data-edge constraints conflict. '
            'No fonts, content, sizes or alignments were changed. Review the requested groups, '
            'choose minimum rather than fixed gaps, or explicitly change the design.')
    # Lexicographic optimization: never trade a larger gutter for a smaller
    # canvas through an arbitrary weighted sum.
    gap_limit=np.zeros(right+1);gap_limit[n:n+nr]=1
    compact=np.zeros(right+1);compact[right]=1
    second=linprog(compact,A_ub=np.vstack([np.array(ub),gap_limit]),
        b_ub=np.r_[bub,result.fun+1e-9],A_eq=np.array(eq) if eq else None,
        b_eq=np.array(beq) if eq else None,bounds=bounds,method='highs')
    if second.success:result=second
    # Resolve free horizontal slack deterministically toward the outer margin;
    # do not leave arbitrary blank space in independently packed short rows.
    right_limit=np.zeros(right+1);right_limit[right]=1
    settle=np.zeros(right+1);settle[:n]=1
    third=linprog(settle,A_ub=np.vstack([np.array(ub),gap_limit,right_limit]),
        b_ub=np.r_[bub,objective@result.x+1e-9,result.x[right]+1e-9],
        A_eq=np.array(eq) if eq else None,b_eq=np.array(beq) if eq else None,
        bounds=bounds,method='highs')
    if third.success:result=third
    left={k:float(result.x[index[k]]) for k in names}
    required_w=float(result.x[right])
    # Reserve a common letter band ABOVE all row content, not just above axes.
    probe=fig.text(0,0,'a',fontsize=style.label,fontweight='bold',va='baseline')
    fig.canvas.draw();pb=probe.get_window_extent(fig.canvas.get_renderer());probe.remove()
    ascent=pb.y1/dpi;descent=max(0,-pb.y0/dpi);pad=label_pad_pt/72
    row_specs=[]
    for row in rows:
        data=[k for k in row if k not in legend_panels]
        top=max([margins[k][3] for k in data]+[0])
        below=max([targets[k][1]+margins[k][2] for k in data]+[0])
        body=max(top+below,max([heights[k] for k in row if k in legend_panels]+[0]))
        band=pad+ascent+descent if data else 0
        row_specs.append((body,top,band))
    required_h=2*outer+sum(b+t for b,_,t in row_specs)+(nr-1)*vertical_gap
    width=required_w; height=required_h
    fig.set_size_inches(width,height);sx=(width-required_w)/2;cursor=height-outer-(height-required_h)/2
    labels={};letter=iter(string.ascii_lowercase)
    for row,(body,top,band) in zip(rows,row_specs):
        body_top=cursor-band;data_top=body_top-top
        for k in row:
            ax=axes[k];ax.set_axes_locator(None)
            if k in legend_panels:
                w,h=widths[k],heights[k];px=left[k]+sx;py=body_top-(body+h)/2
                ax.set_position([px/width,py/height,w/width,h/height])
                legend_panels[k].set_bbox_to_anchor((.5,.5),transform=ax.transAxes)
                legend_panels[k].set_loc('center')
                continue
            w,h=targets[k];px=left[k]+sx+margins[k][0];py=data_top-h
            ax.set_position([px/width,py/height,w/width,h/height]);ax._abs_measured_target=targets[k]
            for extra,(dx,dy,ew,eh) in offsets[k]:
                extra.set_axes_locator(None);extra.set_position([(px+dx)/width,(py+dy)/height,ew/width,eh/height])
            labels[k]=fig.text((left[k]+sx)/width,(body_top+pad+descent)/height,next(letter),
                fontsize=style.label,fontweight='bold',ha='left',va='baseline',gid='abs1-panel-label')
        cursor-=body+band+vertical_gap
    fig.canvas.draw();renderer=fig.canvas.get_renderer();actual={};full={}
    for k in names:
        if k in legend_panels:
            box=legend_panels[k].get_window_extent(renderer)
        else:
            ax=axes[k];box=ax.get_window_extent(renderer)
            if not np.allclose([box.width/dpi,box.height/dpi],targets[k],atol=1e-7,rtol=0):
                raise LayoutConflict(f'{k}: an aspect constraint or locator changed its target data rectangle')
            boxes=[ax.get_tightbbox(renderer)]+[a.get_tightbbox(renderer) for a in attachments.get(k,())]
            box=Bbox.union([b for b in boxes if b is not None])
        actual[k]=[box.x0/dpi,box.y0/dpi,box.x1/dpi,box.y1/dpi]
        full[k]=actual[k][:]
        if k in labels:
            lb=labels[k].get_window_extent(renderer)
            full[k]=[min(full[k][0],lb.x0/dpi),min(full[k][1],lb.y0/dpi),
                     max(full[k][2],lb.x1/dpi),max(full[k][3],lb.y1/dpi)]
    gaps=[]
    for r,row in enumerate(rows):
        values=[actual[b][0]-actual[a][2] for a,b in zip(row,row[1:])]
        if values and (min(values)<horizontal_gap-1e-6 or np.ptp(values)>1e-6):
            raise LayoutConflict('Rendered geometry changed after solving; remeasure text and attachments')
        gaps.append(values)
    vgaps=[min(full[k][1] for k in a)-max(full[k][3] for k in b) for a,b in zip(rows,rows[1:])]
    if any(g<vertical_gap-1e-6 for g in vgaps):raise LayoutConflict('Rendered row contents overlap their reserved gutter')
    for k,box in full.items():
        if box[0]<-1e-6 or box[1]<-1e-6 or box[2]>width+1e-6 or box[3]>height+1e-6:
            raise LayoutConflict(f'{k}: rendered content exceeds the canvas')
    report=dict(mode='measured',canvas_inches=[width,height],required_inches=[required_w,required_h],
        targets_inches={k:list(v) for k,v in targets.items()},content_bounds_inches=actual,
        labelled_bounds_inches=full,horizontal_gaps_inches=gaps,vertical_gaps_inches=vgaps,
        gap_mode=gap_mode,columns=columns,row_data_panel_counts=row_counts,
        effective_column_groups=effective_columns,effective_plot_column_groups=effective_plot_columns,
        column_anchor_scope='Same data-panel count only; legend containers excluded',
        spacing_reasons=[{'row':r,'minimum_inches':horizontal_gap,
            'solved_inches':float(result.x[n+r]),
            'reason':'Minimum reached' if result.x[n+r]<=horizontal_gap+1e-6 else
            'Required by declared shared column anchors/data-edge groups and row adjacency constraints'}
            for r in range(nr)],
        constraints_relaxed=[],content_changes=[],rounding='None; exact content extent plus specified outer margins')
    fig._abs_measured_layout=report
    if hasattr(fig,'_abs_unit_layout'):
        fig._abs_unit_layout['canvas_inches']=[width,height]
        fig._abs_unit_layout['mode']='measured'
    return report
