"""Cut the website's video clips from the trailer (needs ffmpeg on PATH).

    py -3 scripts/site-build/clips.py "C:/path/to/Tryll_Main_final.mp4"

For every clip in config.CLIPS it writes assets/video/<name>.mp4 (plus
<name>-small.mp4 when the clip has a "small" size) and a <name>.jpg poster.
Clips are cut from the trailer without its subtitles (their lines show as
captions on the page instead); a clip with its own "source" from that file.
--only=name[,name] cuts just those clips (no trailer needed for one with its
own source). Then run build.py. Clips are H.264 with +faststart; only clips
marked "audio" keep their sound.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import config as C  # noqa: E402

OUT = os.path.join(ROOT, 'assets', 'video')


def graph(clip, w, h):
    """filter_complex: each shot trimmed, cropped and scaled, then joined."""
    parts, labels = [], ''
    audio = clip.get('audio', False)
    fps = f'fps={clip["fps"]},' if clip.get('fps') else ''   # e.g. a 60 fps screen recording at 30
    shots = clip['shots']
    for i, (start, end, crop) in enumerate(shots):
        parts.append(f'[0:v]trim={start}:{end},setpts=PTS-STARTPTS,{fps}crop={crop},'
                     f'scale={w}:{h}:flags=lanczos,setsar=1[v{i}]')
        labels += f'[v{i}]'
        if audio:
            # Short fades so a clip played with sound doesn't click at a cut; none between
            # shots that follow on in the trailer (a reframe), where the sound carries on.
            fades = ''
            if i == 0 or shots[i - 1][1] != start:
                fades += ',afade=t=in:d=0.04'
            if i == len(shots) - 1 or shots[i + 1][0] != end:
                fades += f',afade=t=out:st={end - start - 0.08:.2f}:d=0.08'
            parts.append(f'[0:a]atrim={start}:{end},asetpts=PTS-STARTPTS{fades}[a{i}]')
            labels += f'[a{i}]'
    parts.append(f'{labels}concat=n={len(shots)}:v=1:a={int(audio)}[v]' + ('[a]' if audio else ''))
    return ';'.join(parts)


def encode(src, clip, size, dst):
    w, h = size
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', graph(clip, w, h), '-map', '[v]',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', str(clip.get('crf', 26)), '-profile:v', 'high',
           '-pix_fmt', 'yuv420p', '-g', '50', '-movflags', '+faststart']
    cmd += ['-map', '[a]', '-c:a', 'aac', '-b:a', '96k'] if clip.get('audio') else ['-an']
    subprocess.run(cmd + [dst], check=True)


def main(src=None, only=None):
    os.makedirs(OUT, exist_ok=True)
    for name, clip in C.CLIPS.items():
        if only and name not in only:
            continue
        if clip.get('source'):   # a recording of its own, not the trailer
            src_of = clip['source']
            if not os.path.exists(src_of):
                print(f'{name}: skipped, {src_of} not found')
                continue
        elif src:
            src_of = src
        else:
            raise SystemExit(f'{name} is cut from the trailer: pass it (or use --only=)')
        mp4 = os.path.join(OUT, name + '.mp4')
        encode(src_of, clip, clip['size'], mp4)
        if clip.get('small'):
            encode(src_of, clip, clip['small'], os.path.join(OUT, name + '-small.mp4'))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(clip.get('poster', 0)), '-i', mp4,
                        '-frames:v', '1', '-q:v', '3', os.path.join(OUT, name + '.jpg')], check=True)
        sizes = ', '.join(f'{f} {os.path.getsize(os.path.join(OUT, f)) // 1024} KB'
                          for f in sorted(os.listdir(OUT)) if f.startswith(name + '.') or f.startswith(name + '-small'))
        print(f'{name}: {sizes}')
    print('done; now run build.py')


if __name__ == '__main__':
    files = [a for a in sys.argv[1:] if not a.startswith('--only=')]
    only = [n for a in sys.argv[1:] if a.startswith('--only=') for n in a[7:].split(',')]
    main(*files[:1], only=only)
