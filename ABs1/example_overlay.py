"""Synthetic data: add points, line, point-line and a band to one caller-owned Axes."""
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
import numpy as np
from abs1.api import (style_context, create_figure, plot_points, plot_line,
                     plot_pointline, plot_fill, set_axis, finalize_layout, save_pdf)


def draw_overlay(ax, x_obs, y_obs, x_fit, y_fit, x_ref, y_ref, lower, upper):
    """Draw into an existing Axes; no figure creation, axes configuration or saving."""
    plot_points(ax, x_obs, y_obs, label='Obs.', zorder=3)
    plot_line(ax, x_fit, y_fit, label='Fit', zorder=2)
    plot_pointline(ax, x_ref, y_ref, label='Ref.', zorder=2)
    # The band belongs to the fitted series, so explicitly reuse its second color.
    plot_fill(ax, x_fit, lower, upper, boundary=False, color_index=1, zorder=1)
    return ax


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qa-dir',type=Path)
    args=parser.parse_args()
    base=Path(__file__).resolve().parent
    stamp=datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y_%m_%d_%H:%M:%S')
    log=base/'Log'/(stamp+'_same-axes-overlay')
    log.mkdir(parents=True,exist_ok=False)
    seed=20261112
    rng=np.random.default_rng(seed)
    x_obs=np.linspace(.15,3.85,9)
    y_obs=.2+.15*x_obs+rng.uniform(-.025,.025,len(x_obs))
    x_fit=np.linspace(.15,3.85,81)
    y_fit=.2+.15*x_fit
    x_ref=np.linspace(.15,3.85,5)
    y_ref=.16+.14*x_ref
    lower,upper=y_fit-.025,y_fit+.025  # Illustrative band, not a confidence interval.
    for name,values,header in [
        ('observations',np.c_[x_obs,y_obs],'x,y'),
        ('fit',np.c_[x_fit,y_fit,lower,upper],'x,y,lower,upper'),
        ('reference',np.c_[x_ref,y_ref],'x,y'),
    ]:
        np.savetxt(log/(name+'.csv'),values,delimiter=',',header=header,comments='')
    with style_context():
        fig,axes=create_figure()
        ax=axes[0,0]  # The caller supplies exactly the same ax to every drawing function.
        result=draw_overlay(ax,x_obs,y_obs,x_fit,y_fit,x_ref,y_ref,lower,upper)
        assert result is ax and fig.axes == [ax]
        set_axis(ax,xlim=(0,4),ylim=(.1,.9),xticks=[0,2,4],yticks=[.1,.5,.9],
                 xlabel='Time',ylabel='Response')
        handles,labels=ax.get_legend_handles_labels()
        order=[labels.index(label) for label in ['Obs.','Fit','Ref.']]
        ax.legend([handles[i] for i in order],[labels[i] for i in order],
                  loc='upper left',labelspacing=.1,borderpad=.1,
                  handlelength=1,handletextpad=.3,borderaxespad=.15)
        finalize_layout(fig,axes)
        if args.qa_dir:
            sys.path.insert(0,str(args.qa_dir.resolve()))
            from audit_panel_alignment import require_matplotlib_panel_alignment
            require_matplotlib_panel_alignment(fig,json_out=str(log/'alignment.json'),strict=True)
        target=save_pdf(fig,'overlay',output_dir=base/'Figure')
        plt.close(fig)
    if args.qa_dir:
        for script,extra in [
            ('audit_pdf_text.py',['--min-pt','5']),
            ('audit_figure_collisions.py',['--json-out',str(log/'collisions.json')]),
        ]:
            result=subprocess.run([sys.executable,str(args.qa_dir/script),str(target),*extra],
                                  capture_output=True,text=True)
            (log/(script+'.txt')).write_text(result.stdout+result.stderr)
            if result.returncode:
                raise RuntimeError(f'{script} failed; see {log}')
    (log/'run.json').write_text(json.dumps(dict(synthetic=True,seed=seed,
        size_inches=[3,2.5],font_pt=14,line_width_pt=1.2,axes_count=1,
        n_observations=len(x_obs),n_fit=len(x_fit),n_reference=len(x_ref),
        band='Illustrative +/-0.025, not a confidence interval',
        qa_enabled=bool(args.qa_dir)),indent=2))
    print(f'{"Saved":<14} {target}')

if __name__=='__main__':
    main()
