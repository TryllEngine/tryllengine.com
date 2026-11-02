"""Cut the website's video clips from the trailer (needs ffmpeg on PATH).

    py -3 scripts/site-build/clips.py "C:/path/to/trailer-with-subtitles.mp4" "C:/path/to/trailer.mp4"

For every clip in config.CLIPS it writes assets/video/<name>.mp4 (plus
<name>-small.mp4 when the clip has a "small" size) and a <name>.jpg poster.
Clips are cut from the first file, which has the subtitles drawn in; clips
marked "clean" from the second, the same trailer without them (their lines
show as captions on the page instead). Then run build.py. Clips are H.264
with +faststart; only clips marked "audio" keep their sound.
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
    for i, (start, end, crop) in enumerate(clip['shots']):
        parts.append(f'[0:v]trim={start}:{end},setpts=PTS-STARTPTS,crop={crop},'
                     f'scale={w}:{h}:flags=lanczos,setsar=1[v{i}]')
        labels += f'[v{i}]'
        if audio:
            # Short fades so a clip played with sound doesn't click at the cut.
            parts.append(f'[0:a]atrim={start}:{end},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,'
                         f'afade=t=out:st={end - start - 0.08:.2f}:d=0.08[a{i}]')
            labels += f'[a{i}]'
    n = len(clip['shots'])
    hold = clip.get('hold')   # seconds the last frame stays on screen, in silence
    v, a = ('[vj]', '[aj]') if hold else ('[v]', '[a]')
    parts.append(f'{labels}concat=n={n}:v=1:a={int(audio)}{v}' + (a if audio else ''))
    if hold:
        parts.append(f'[vj]tpad=stop_mode=clone:stop_duration={hold}[v]')
        if audio:
            parts.append(f'[aj]apad=pad_dur={hold}[a]')
    return ';'.join(parts)


def encode(src, clip, size, dst):
    w, h = size
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', graph(clip, w, h), '-map', '[v]',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', str(clip.get('crf', 26)), '-profile:v', 'high',
           '-pix_fmt', 'yuv420p', '-g', '50', '-movflags', '+faststart']
    cmd += ['-map', '[a]', '-c:a', 'aac', '-b:a', '96k'] if clip.get('audio') else ['-an']
    subprocess.run(cmd + [dst], check=True)


def main(src, clean=None):
    os.makedirs(OUT, exist_ok=True)
    for name, clip in C.CLIPS.items():
        if clip.get('clean'):
            if not clean:
                raise SystemExit(f'{name} is cut from the trailer without subtitles: pass that file second')
            src_of = clean
        else:
            src_of = src
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
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
