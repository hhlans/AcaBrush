"""Render a palette card as PDF; import and plotting styles remain caller-controlled."""
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
from matplotlib.patches import Rectangle

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parent/'ABs1'))
from abs1.api import (get_palette, style_context, create_figure,
                     finalize_layout, save_pdf)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name',nargs='?',default='reference12')
    parser.add_argument('--qa-dir',type=Path)
    args=parser.parse_args()
    colors=get_palette(args.name)
    columns=min(6,len(colors))
    rows=(len(colors)+columns-1)//columns
    stamp=datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y_%m_%d_%H:%M:%S')
    log=BASE/'Log'/(stamp+'_palette-card_'+args.name)
    log.mkdir(parents=True,exist_ok=False)
    with style_context():
        fig,axes=create_figure(rows,columns)
        for i,ax in enumerate(axes.flat):
            ax.set_axis_off()
            if i >= len(colors):
                continue
            color=colors[i]
            rgb=tuple(int(color[j:j+2],16) for j in (1,3,5))
            ax.add_patch(Rectangle((.07,.43),.86,.48,transform=ax.transAxes,
                                   facecolor=color,edgecolor='none'))
            ax.text(.07,.30,f'{i:02d}  {color}',transform=ax.transAxes)
            ax.text(.07,.12,f'RGB {rgb[0]}, {rgb[1]}, {rgb[2]}',transform=ax.transAxes)
        finalize_layout(fig,axes)
        if args.qa_dir:
            sys.path.insert(0,str(args.qa_dir.resolve()))
            from audit_panel_alignment import require_matplotlib_panel_alignment
            require_matplotlib_panel_alignment(fig,json_out=str(log/'alignment.json'),strict=True)
        target=save_pdf(fig,args.name,output_dir=BASE/'Figure')
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
    (log/'run.json').write_text(json.dumps(dict(palette=args.name,colors=list(colors),
        size_inches=list(fig.get_size_inches()),qa_enabled=bool(args.qa_dir)),indent=2))
    print(f'{"Saved":<14} {target}')

if __name__=='__main__':
    main()
