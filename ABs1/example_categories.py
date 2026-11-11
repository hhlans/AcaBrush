"""Synthetic demonstration of five chart families; no experimental claims."""
import argparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import subprocess
import sys
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from abs1.api import (style_context, create_figure, plot_points, plot_line,
                     plot_pointline, plot_fill, plot_bar, plot_heatmap,
                     plot_violin, finalize_layout, save_pdf, DEFAULT, get_palette, get_cmap)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qa-dir', type=Path)
    parser.add_argument('--palette', default='reference12', help='ABsCol palette, e.g. reference12 or reference12_warm')
    args = parser.parse_args()
    selected_colors = list(get_palette(args.palette)) if args.palette else None

    def colors():
        return dict(palette=args.palette)

    base = Path(__file__).resolve().parent
    stamp = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y_%m_%d_%H:%M:%S')
    log = base / 'Log' / (stamp + '_five-chart-families_' + (args.palette or 'default'))
    log.mkdir(parents=True)
    start = time.perf_counter()
    seed = 20261111
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 4, 17)
    y = .2 + .15*x
    observations = y + rng.uniform(-.06, .06, len(x))
    means, errors = np.array([.3, .5, .7]), np.array([.04, .05, .06])
    matrix = np.linspace(0, 1, 24).reshape(4, 6)
    groups = [rng.beta(3, 7, 40), rng.beta(5, 5, 40), rng.beta(7, 3, 40)]
    np.savetxt(log/'curves.csv', np.c_[x,y,observations], delimiter=',',
               header='x,curve,observation', comments='')
    np.savetxt(log/'bars.csv', np.c_[means,errors], delimiter=',',
               header='mean,illustrative_error', comments='')
    np.savetxt(log/'heatmap.csv', matrix, delimiter=',')
    np.savetxt(log/'violin.csv', np.asarray(groups).T, delimiter=',',
               header='A,B,C', comments='')
    print(f'{"Stage":<14} {"Details":<55}')
    print(f'{"Render":<14} {"Five chart families | synthetic data | 14 pt":<55}')
    with style_context():
        # Keep the global default: each panel occupies 3 x 2.5 inches.
        fig, axes = create_figure(2, 3)
        a,b,c,d,e,f = axes.flat
        plot_points(a,x,observations,**colors())
        plot_line(b,x,y, label='Line',**colors())
        plot_pointline(b,x,y-.12, label='Point-line',**colors())
        b.legend(loc='upper left', handlelength=1.1, borderaxespad=.15,
                 labelspacing=.2, borderpad=.15, handletextpad=.4)
        plot_fill(c,x,y-.08,y+.08,**colors())
        plot_bar(d,[1,2,3],means,yerr=errors,**colors())
        heatmap_options = dict(palette=args.palette, continuous=True)
        plot_heatmap(e,np.arange(7),np.arange(5),matrix,vmin=0,vmax=1,**heatmap_options)
        plot_violin(f,groups,positions=[1,2,3],**colors())
        for ax in (a,b,c):
            ax.set(xlim=(0,4),ylim=(0,1),xticks=[0,2,4],yticks=[0,.5,1],
                   xlabel='Time',ylabel='Response')
        for ax in (d,f):
            ax.set(xlim=(.5,3.5),ylim=(0,1),yticks=[0,.5,1],
                   xlabel='Group',ylabel='Response')
            ax.set_xticks([1,2,3],['A','B','C'])
        e.set(xlim=(0,6),ylim=(0,4),xticks=[0,3,6],yticks=[0,2,4],
              xlabel='Column',ylabel='Row')
        # Reserve colorbar space only inside the heatmap's own subplot slot.
        divider = make_axes_locatable(e)
        cax = divider.append_axes("right", size="5%", pad=0.08)
        cb=fig.colorbar(e.collections[-1],cax=cax,ticks=[0,.5,1])
        cb.ax.tick_params(labelsize=DEFAULT.font,width=DEFAULT.tick,length=DEFAULT.tick_length)
        cb.outline.set_linewidth(DEFAULT.axes)
        finalize_layout(fig, axes)
        if args.qa_dir:
            sys.path.insert(0,str(args.qa_dir.resolve()))
            from audit_panel_alignment import require_matplotlib_panel_alignment
            require_matplotlib_panel_alignment(fig,json_out=str(log/'alignment.json'),
                exclude_axes=[cax], tolerance_pt=1.5,gutter_tolerance_pt=1.5,strict=True,
                exemptions=[dict(panels=["e"],
                    checks=["column", "panel-width", "horizontal-gutter"],
                    reason="Only the heatmap reserves part of its default subplot slot for its colorbar")])
        target=save_pdf(fig,'categories' + ('_'+args.palette if args.palette else ''),output_dir=base/'Figure')
        if args.palette == 'reference12':
            (base/'Figure/categories.pdf').write_bytes(target.read_bytes())
        plt.close(fig)
    if args.qa_dir:
        for script,extra in [
            ('audit_pdf_text.py',['--min-pt','5']),
            ('audit_figure_collisions.py',['--json-out',str(log/'collisions.json')]),
        ]:
            result=subprocess.run([sys.executable,str(args.qa_dir/script),str(target),*extra],
                                  text=True,capture_output=True)
            (log/(script+'.txt')).write_text(result.stdout+result.stderr)
            if result.returncode:
                raise RuntimeError(f'{script} failed; see {log}')
    (log/'run.json').write_text(json.dumps(dict(synthetic=True,seed=seed,palette=args.palette,palette_colors=selected_colors,
        panel_roles=['points','line and point-line','interval fill','bars with illustrative errors',
                     'heatmap','sample distributions'],
        size_inches=list(fig.get_size_inches()),
        panel_size_inches=[3,2.5], font_pt=DEFAULT.font, panel_label_pt=DEFAULT.label,
        line_width_pt=DEFAULT.line, layout_w_pad=1.1, layout_h_pad=2.0,python=sys.version,matplotlib=matplotlib.__version__,
        numpy=np.__version__,qa_enabled=bool(args.qa_dir),
        elapsed_seconds=round(time.perf_counter()-start,3)),indent=2))
    print(f'{"Saved":<14} {target}')

if __name__=='__main__':
    main()
