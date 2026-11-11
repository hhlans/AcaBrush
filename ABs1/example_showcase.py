"""Rich 12-group synthetic showcase. All observations are simulated, not experimental.

Panels use individual whole-cell spans from configs/showcase-layout.json.
The fixed 3x2.8 inch unit grid determines the complete canvas automatically.
Global fonts, strokes and marker sizes are unchanged. Every panel restarts its
palette; corresponding groups retain identical colors across all panels.
"""
import argparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import subprocess
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
# All data drawing enters the user's AcaBrush API and delegates to figure_plot.py.
from abs1 import api as brush


def make_data(seed=20261115):
    rng=np.random.default_rng(seed)
    time=np.linspace(.3,23.7,97)
    group=np.arange(12)
    trajectories=np.array([10+4*g+(20+2*g)*(1-np.exp(-(g+3)*time/70))+
                           2*np.sin(time/3+.6*g) for g in group])
    angle=group*2*np.pi/12
    centers=np.c_[2.35*np.cos(angle),2.35*np.sin(angle)]
    clusters=np.array([rng.normal(size=(48,2))*[.15,.12]+center for center in centers])
    raw=np.array([(1+.12*g)*(1+.42*np.sin(time/4+g*.55)+.12*np.cos(time/2+g))
                  for g in group])
    shares=100*raw/raw.sum(axis=0)
    bar_means=np.array([.28+.039*group+.07*j+.025*np.sin(group+j) for j in range(3)])
    bar_sd=.018+.009*rng.random((3,12))
    heat_time=np.linspace(0,24,36)
    heat=np.array([.58*np.sin(2*np.pi*heat_time/24+g*.32)+
                   .35*np.cos(np.pi*heat_time/24+g*.58) for g in group])
    samples=np.array([rng.beta(2+.6*g,9-.35*g,size=36) for g in group])
    jitter=rng.uniform(-.12,.12,samples.shape)
    return dict(time=time,trajectories=trajectories,clusters=clusters,
                shares=shares,bar_means=bar_means,bar_sd=bar_sd,
                heat=heat,samples=samples,jitter=jitter)


def draw_profiles(ax,d):
    for i,y in enumerate(d['trajectories']):
        brush.plot_pointline(ax,d['time'],y,markevery=8,label=f'G{i+1:02}')


def draw_clusters(ax,d):
    for i,points in enumerate(d['clusters']):
        brush.plot_points(ax,points[:,0],points[:,1],alpha=.85,rasterized=True,label=f'G{i+1:02}')


def draw_composition(ax,d):
    bottom=np.zeros_like(d['time'])
    for values in d['shares']:
        brush.plot_fill(ax,d['time'],bottom,bottom+values,boundary=False,alpha=1)
        bottom=bottom+values


def draw_bars(ax,d):
    x=np.arange(1,13)
    for condition,alpha in enumerate([1,.66,.34]):
        # 12 bars consume one complete palette, so subsequent conditions repeat it.
        brush.plot_bar(ax,x+(condition-1)*.24,d['bar_means'][condition],
                 yerr=d['bar_sd'][condition],width=.22,capsize=1.8,
                 alpha=alpha)


def draw_heat(ax,d):
    brush.plot_heatmap(ax,np.linspace(0,24,37),np.arange(13),d['heat'],
                 vmin=-1,vmax=1,palette='reference12_heat',continuous=True)


def draw_distributions(ax,d):
    brush.plot_violin(ax,d['samples'],positions=np.arange(1,13),widths=.72,alpha=.8)
    for i,values in enumerate(d['samples']):
        brush.plot_points(ax,i+1+d['jitter'][i],values,color_index=i,
                    alpha=.28,zorder=3,rasterized=True)


def run_pdf_checks(pdf,log,qa_dir):
    if qa_dir is None:
        return
    for script,extra in [('audit_pdf_text.py',['--min-pt','5']),
        ('audit_figure_collisions.py',['--json-out',str(log/(pdf.stem+'.collisions.json'))])]:
        result=subprocess.run([sys.executable,str(qa_dir/script),str(pdf),*extra],
                              capture_output=True,text=True)
        (log/(pdf.stem+'.'+script+'.txt')).write_text(result.stdout+result.stderr)
        if result.returncode:
            raise RuntimeError(f'{script} failed; see {log}')


def render_showcase(d,base,log,qa_dir):
    with brush.style_context():
        plan=json.loads((base/'configs/showcase-layout.json').read_text())
        if tuple(plan['base_inches']) != brush.BASE_PANEL_SIZE:
            raise ValueError('The layout must use the fixed 3 x 2.8 inch base unit')
        fig,panels=brush.create_layout(plan['mosaic'])
        axes=np.array([panels[key] for key in 'abcdef'],dtype=object)
        a,b,c,e_bar,e_heat,f=axes
        panels['legend'].set_axis_off()
        for draw,ax in zip([draw_profiles,draw_clusters,draw_composition,draw_bars,
                            draw_heat,draw_distributions],axes.flat):
            draw(ax,d)
        a.set(xlim=(0,24),ylim=(0,100),xticks=[0,12,24],yticks=[0,50,100],
              xlabel='Time (h)',ylabel='Signal')
        b.set(xlim=(-3,3),ylim=(-3,3),xticks=[-3,0,3],yticks=[-3,0,3],
              xlabel='Feature 1',ylabel='Feature 2')
        c.set(xlim=(0,24),ylim=(0,100),xticks=[0,12,24],yticks=[0,50,100],
              xlabel='Time (h)',ylabel='Composition (%)')
        e_bar.set(xlim=(.4,12.6),ylim=(0,1),xticks=np.arange(1,13),yticks=[0,.5,1],
                  xlabel='Group',ylabel='Response')
        condition_handles=[Patch(facecolor=brush.get_palette('reference12')[1],
                                 edgecolor='none',alpha=alpha,label=label)
                           for alpha,label in zip([1,.66,.34],['A','B','C'])]
        e_bar.legend(handles=condition_handles,loc='upper left',ncol=3,
                     handlelength=1,borderpad=.2,columnspacing=1)
        e_heat.set(xlim=(0,24),ylim=(0,12),xticks=[0,12,24],
                   xlabel='Time (h)',ylabel='Group')
        e_heat.set_yticks([.5,3.5,7.5,11.5],['1','4','8','12'])
        f.set(xlim=(.4,12.6),ylim=(0,1),xticks=np.arange(1,13),yticks=[0,.5,1],
              xlabel='Group',ylabel='Response')
        divider=make_axes_locatable(e_heat)
        cax=divider.append_axes('right',size='4%',pad=.10)
        cb=fig.colorbar(e_heat.collections[-1],cax=cax,ticks=[-1,0,1])
        cb.ax.tick_params(labelsize=brush.DEFAULT.font,width=brush.DEFAULT.tick,length=brush.DEFAULT.tick_length)
        cb.outline.set_linewidth(brush.DEFAULT.axes)
        colors=brush.get_palette('reference12');markers=brush.load_config('point-line')['markers']
        handles=[Line2D([],[],color=color,marker=markers[i%len(markers)],
                        linewidth=brush.DEFAULT.line,markersize=brush.DEFAULT.marker,label=f'G{i+1:02}')
                 for i,color in enumerate(colors)]
        panels['legend'].legend(handles=handles,loc='center',
                   ncol=2,frameon=False,columnspacing=1.2,handlelength=2,
                   handletextpad=.5,labelspacing=.9)
        brush.finalize_layout(fig,axes)
        layout=brush.get_layout_spec(fig)
        (log/'showcase.layout.json').write_text(json.dumps(layout,indent=2))
        if qa_dir:
            sys.path.insert(0,str(qa_dir.resolve()))
            from audit_panel_alignment import require_matplotlib_panel_alignment
            require_matplotlib_panel_alignment(fig,json_out=str(log/'showcase.alignment.json'),
                exclude_axes=[cax,panels["legend"]],strict=True,tolerance_pt=1.5,gutter_tolerance_pt=1.5,
                exemptions=[dict(panels=['e'],checks=['column','panel-width','horizontal-gutter'],
                    reason='Only heatmap e reserves part of its subplot slot for its colorbar')])
        pdf=brush.save_pdf(fig,'showcase_reference12',output_dir=base/'Figure')
        plt.close(fig)
    run_pdf_checks(pdf,log,qa_dir)
    return pdf,layout


def render_gradient(base,log,qa_dir):
    colors=brush.get_palette('reference12_heat')
    with brush.style_context():
        fig,axes=brush.create_figure(panel_size=(12,2.8))
        ax=axes[0,0]
        brush.plot_heatmap(ax,np.linspace(0,1,1025),[.37,.85],
                           np.linspace(0,1,1024)[None,:],
                           palette='reference12_heat',continuous=True,vmin=0,vmax=1)
        for i,(position,color) in enumerate(zip(np.linspace(0,1,len(colors)),colors)):
            align='left' if i==0 else ('right' if i==len(colors)-1 else 'center')
            ax.text(position,.15,color,ha=align,va='center')
            brush.plot_line(ax,[position,position],[.31,.36],color=color)
        ax.set(xlim=(-.015,1.015),ylim=(0,1));ax.set_axis_off()
        brush.finalize_layout(fig,axes)
        pdf=brush.save_pdf(fig,'showcase_bluepink_gradient',output_dir=base/'Figure')
        plt.close(fig)
    run_pdf_checks(pdf,log,qa_dir)
    return pdf


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qa-dir',type=Path)
    args=parser.parse_args()
    base=Path(__file__).resolve().parent
    stamp=datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y_%m_%d_%H:%M:%S')
    log=base/'Log'/(stamp+'_twelve-group-showcase')
    log.mkdir(parents=True,exist_ok=False)
    data=make_data()
    np.savez_compressed(log/'synthetic_data.npz',**data)
    for key in ['trajectories','shares','bar_means','bar_sd','heat','samples']:
        np.savetxt(log/(key+'.csv'),data[key],delimiter=',')
    assert np.allclose(data['shares'].sum(axis=0),100)
    assert np.max(np.abs(data['clusters']))<3
    assert data['trajectories'].min()>0 and data['trajectories'].max()<100
    assert (data['bar_means']+data['bar_sd']).max()<1
    assert np.max(np.abs(data['heat']))<1
    print('Rendering 12-group showcase and six-anchor blue-pink gradient')
    pdf,layout=render_showcase(data,base,log,args.qa_dir)
    gradient=render_gradient(base,log,args.qa_dir)
    (log/'run.json').write_text(json.dumps(dict(synthetic=True,seed=20261115,
        groups=12,cluster_points=576,bar_count=36,violin_observations=432,
        palette=list(brush.get_palette('reference12')),heat_anchors=list(brush.get_palette('reference12_heat')),
        canvas_inches=layout['canvas_inches'],
        panel_units={name:[p['width_units'],p['height_units']] for name,p in layout['panels'].items()},
        font_pt=brush.DEFAULT.font,line_width_pt=brush.DEFAULT.line,
        panel_roles=['trajectories','feature clusters','composition','three-condition response',
                     'response deviation matrix','distributions with all observations'],
        qa_enabled=bool(args.qa_dir)),indent=2))
    print(pdf);print(gradient)

if __name__=='__main__':
    main()
