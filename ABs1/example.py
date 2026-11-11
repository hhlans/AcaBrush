"""2x2 synthetic example: response, validation, error, boundary. No experimental claim."""
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
import json
from pathlib import Path
import subprocess
import sys
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from abs1.api import (style_context, create_figure, plot_line, plot_points, plot_pointline, set_axis,
                 finalize_layout, save_pdf, COLORS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qa-dir', type=Path,
                        help='nature-figure/scripts directory; enables full audits')
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    stamp = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y_%m_%d_%H:%M:%S')
    log = base / 'Log' / (stamp + '_synthetic-demo')
    log.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    seed = 20261110
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 10, 21)
    truth = 1 - np.exp(-x / 3)
    predicted = truth + rng.normal(0, .025, len(x))
    residual = predicted - truth
    noise = np.linspace(0, .5, 11)
    error = .02 + .25 * noise**2
    np.savetxt(log / 'synthetic_response.csv', np.c_[x, truth, predicted, residual],
               delimiter=',', header='time,truth,predicted,residual', comments='')
    np.savetxt(log / 'synthetic_boundary.csv', np.c_[noise, error],
               delimiter=',', header='noise,error', comments='')
    print(f'{"Stage":<14} {"Details":<55}')
    print(f'{"Render":<14} {"2x2 | 6x5 inch | 14 pt | synthetic data":<55}')
    with style_context():
        fig, axes = create_figure(2, 2)
        a, b, c, d = axes.flat
        plot_pointline(a, x, truth)
        set_axis(a, xlim=(0, 10), ylim=(0, 1), xticks=[0, 5, 10],
                 yticks=[0, .5, 1], xlabel='Time', ylabel='Response')
        plot_points(b, truth, predicted)
        plot_line(b, [0, 1], [0, 1], ls='--')
        set_axis(b, xlim=(-.05, 1.05), ylim=(-.05, 1.05),
                 xticks=[-.05, .5, 1.05], yticks=[-.05, .5, 1.05],
                 xlabel='True value', ylabel='Prediction')
        plot_pointline(c, x, residual)
        plot_line(c, [0, 10], [0, 0], ls='--')
        set_axis(c, xlim=(0, 10), ylim=(-.07, .07), xticks=[0, 5, 10],
                 yticks=[-.07, 0, .07], xlabel='Time', ylabel='Residual')
        plot_pointline(d, noise, error)
        set_axis(d, xlim=(0, .5), ylim=(.018, .084), xticks=[0, .25, .5],
                 yticks=[.018, .051, .084], xlabel='Noise level', ylabel='Error')
        for ax in axes.flat:
            for line in ax.lines:
                for values, limits in ((line.get_xdata(), ax.get_xlim()),
                                       (line.get_ydata(), ax.get_ylim())):
                    assert np.min(values) >= limits[0] and np.max(values) <= limits[1], \
                        "Axis limits must cover every synthetic observation"
        finalize_layout(fig, axes)
        if args.qa_dir:
            sys.path.insert(0, str(args.qa_dir.resolve()))
            from audit_panel_alignment import require_matplotlib_panel_alignment
            require_matplotlib_panel_alignment(
                fig, json_out=str(log / 'alignment.json'),
                tolerance_pt=1.5, gutter_tolerance_pt=1.5, strict=True)
        target = save_pdf(fig, 'example', output_dir=base / 'Figure')
        plt.close(fig)
    if args.qa_dir:
        commands = [
            ['audit_pdf_text.py', str(target), '--min-pt', '5'],
            ['audit_figure_collisions.py', str(target), '--json-out',
             str(log / 'collisions.json')],
        ]
        for command in commands:
            result = subprocess.run([sys.executable, str(args.qa_dir / command[0]),
                                     *command[1:]], capture_output=True, text=True)
            (log / (command[0] + '.txt')).write_text(result.stdout + result.stderr)
            if result.returncode:
                raise RuntimeError(f'Audit failed: {command[0]}; see {log}')
    metadata = dict(synthetic=True, seed=seed, size_inches=[6, 5],
                    python=sys.version, matplotlib=matplotlib.__version__,
                    numpy=np.__version__, qa_enabled=bool(args.qa_dir),
                    elapsed_seconds=round(time.perf_counter()-start, 3))
    (log / 'run.json').write_text(json.dumps(metadata, indent=2))
    print(f'{"Saved":<14} {str(target):<55}')

if __name__ == '__main__':
    main()
