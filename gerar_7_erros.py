"""JUH QUIZ — jogo dos 7 erros, três layouts em sequência automática.

python gerar_7_erros.py
python gerar_7_erros.py --previas
Requer Pillow e FFmpeg. Veja LEIA_ME.md para inserir seus desafios.
"""
import argparse
import json
import math
import re
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE = Path(__file__).resolve().parent
W, H = 1080, 1920
MODELOS = [
    dict(nome="rosa", fundo="#ff258d", escuro="#880b46", destaque="#fff02e"),
    dict(nome="azul", fundo="#066af0", escuro="#061e75", destaque="#ffe62c"),
    dict(nome="roxo", fundo="#6020c7", escuro="#321069", destaque="#ff40ae"),
]
CAIXAS = [(36, 405, 1044, 1005), (36, 1035, 1044, 1635)]

def modelo_do_video(numero):
    if numero < 1:
        raise ValueError("Número de vídeo deve começar em 1.")
    return MODELOS[(numero - 1) % 3]

def fonte(tamanho):
    for p in [BASE / "fontes/DejaVuSans-Bold.ttf",
              Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
              Path("C:/Windows/Fonts/arialbd.ttf")]:
        if p.exists():
            return ImageFont.truetype(str(p), tamanho)
    raise RuntimeError("Coloque DejaVuSans-Bold.ttf na pasta fontes.")

def texto(d, valor, y, tamanho, cor, contorno=None, largura=990):
    f = fonte(tamanho)
    while d.textbbox((0, 0), valor, font=f)[2] > largura and tamanho > 16:
        tamanho -= 1
        f = fonte(tamanho)
    d.text((W // 2, y), valor, font=f, fill=cor, anchor="mt",
           stroke_width=5 if contorno else 0, stroke_fill=contorno)

def carregar(p):
    with Image.open(p) as img:
        return ImageOps.exif_transpose(img).convert("RGB")

def validar(item):
    for k in ["titulo", "imagem_a", "imagem_b", "erros"]:
        if k not in item:
            raise ValueError(f"Desafio sem campo {k}.")
    if len(item["erros"]) != 7:
        raise ValueError("Cada desafio precisa de exatamente sete erros.")
    for e in item["erros"]:
        if not (0 <= e["x"] <= 1 and 0 <= e["y"] <= 1 and 0 < e["raio"] < 0.5):
            raise ValueError("Coordenadas/raio inválidos: use valores proporcionais de 0 a 1.")
        if not e.get("descricao"):
            raise ValueError("Cada erro precisa de descrição.")
    a, b = carregar(BASE / item["imagem_a"]), carregar(BASE / item["imagem_b"])
    if a.size != b.size:
        raise ValueError("As duas imagens precisam ter a mesma dimensão e enquadramento.")
    if a.tobytes() == b.tobytes():
        raise ValueError("As duas imagens são idênticas.")
    return a, b

def quadro(item, numero, imagens, segundos=None, resposta=False):
    m = modelo_do_video(numero)
    img = Image.new("RGB", (W, H), m["fundo"])
    d = ImageDraw.Draw(img)
    # Formas discretas no fundo, sem invadir as cenas.
    for x, y in [(45, 70), (1010, 210), (28, 1810), (1020, 1810)]:
        d.ellipse((x-55, y-55, x+55, y+55), fill=m["escuro"])
    texto(d, "JUH QUIZ", 42, 63, "white", m["escuro"])
    texto(d, "JOGO DOS 7 ERROS", 140, 89, "white", m["escuro"])
    d.rounded_rectangle((95, 270, 985, 350), 32, fill=m["destaque"])
    texto(d, "Confira as respostas!" if resposta else "Encontre as diferenças!",
          286, 43, "white" if m["nome"] == "roxo" else m["escuro"], largura=850)
    for idx, (im, box) in enumerate(zip(imagens, CAIXAS)):
        x0, y0, x1, y1 = box
        d.rounded_rectangle((x0-8, y0-8, x1+8, y1+8), 36, fill="white")
        # Contain preserva toda a imagem, sem cortes nas diferenças.
        fit = ImageOps.contain(im, (x1-x0, y1-y0))
        ox, oy = x0+(x1-x0-fit.width)//2, y0+(y1-y0-fit.height)//2
        img.paste(fit, (ox, oy))
        if resposta:
            for n, e in enumerate(item["erros"], 1):
                cx, cy = ox+e["x"]*fit.width, oy+e["y"]*fit.height
                r = e["raio"] * min(fit.size)
                d.ellipse((cx-r, cy-r, cx+r, cy+r), outline="#ff163b", width=6)
                d.ellipse((cx+r-15, cy-r-16, cx+r+23, cy-r+22), fill="#ff163b")
                d.text((cx+r+4, cy-r+3), str(n), font=fonte(23), anchor="mm", fill="white")
        d.ellipse((x0+9, y0+9, x0+87, y0+87), fill=m["destaque"])
        d.text((x0+48, y0+48), "AB"[idx], font=fonte(51), anchor="mm", fill=m["escuro"])
    d.rounded_rectangle((55, 1680, 1025, 1805), 48, fill="white")
    d.rounded_rectangle((70, 1694, 395, 1790), 38, fill=m["destaque"])
    d.text((233, 1742), "RESPOSTA" if resposta else f"00:{segundos:02d}",
           font=fonte(36 if resposta else 63), anchor="mm", fill=m["escuro"])
    for i in range(7):
        cx = 465+i*78
        d.ellipse((cx-25, 1717, cx+25, 1767), outline=m["escuro"], width=4,
                  fill=m["destaque"] if resposta else "white")
        if resposta:
            d.text((cx, 1742), str(i+1), font=fonte(26), anchor="mm", fill=m["escuro"])
    texto(d, "Quantos você encontrou?", 1840, 45, "white", m["escuro"])
    return img

def audio_tick(caminho, tempo, revelacao):
    """Áudio original simples: toque por segundo e sinal na revelação."""
    import array
    taxa = 44100
    dados = array.array("h")
    for s in range(tempo + revelacao):
        freq = 1100 if s == tempo else 700
        for j in range(taxa):
            t = j / taxa
            dur = 0.35 if s == tempo else 0.07
            amp = 0.16 * max(0, 1-t/dur) if s <= tempo and t < dur else 0
            dados.append(int(32767*amp*math.sin(2*math.pi*freq*t)))
    import sys
    if sys.byteorder != "little":
        dados.byteswap()
    with wave.open(str(caminho), "wb") as arq:
        arq.setnchannels(1)
        arq.setsampwidth(2)
        arq.setframerate(taxa)
        arq.writeframes(dados.tobytes())

def gerar_video(item, numero, saida, tempo, revelacao, previas=False):
    imagens = validar(item)
    nome = f"jogo_{numero:03d}_{modelo_do_video(numero)['nome']}"
    quadro(item, numero, imagens, tempo).save(saida / f"{nome}_capa.png")
    quadro(item, numero, imagens, resposta=True).save(saida / f"{nome}_resposta.png")
    legenda = item.get("legenda", "Você consegue encontrar os 7 erros? Comente quantos encontrou!")
    (saida / f"{nome}.txt").write_text(
        f"CAPA_SEGUNDOS=2\n\n{legenda}\n#JuhQuiz #7Erros #DesafioVisual #Kwai\n", encoding="utf-8")
    (saida / f"{nome}_gabarito.txt").write_text(
        "\n".join(f"{i}. {e['descricao']}" for i, e in enumerate(item['erros'], 1)), encoding="utf-8")
    if previas:
        return
    with tempfile.TemporaryDirectory(prefix="juh_7_erros_") as pasta:
        tmp = Path(pasta)
        audio_tick(tmp / "audio.wav", tempo, revelacao)
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", "1", "-i", "pipe:0", "-i", str(tmp / "audio.wav"),
               "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-r", "30",
               "-pix_fmt", "yuv420p", "-vf", "setsar=1", "-c:a", "aac", "-b:a", "128k",
               "-shortest", "-movflags", "+faststart", str(saida / f"{nome}.mp4")]
        with (tmp / "ffmpeg.log").open("wb") as log:
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
            try:
                for restante in range(tempo, 0, -1):
                    proc.stdin.write(quadro(item, numero, imagens, restante).tobytes())
                final = quadro(item, numero, imagens, resposta=True).tobytes()
                for _ in range(revelacao):
                    proc.stdin.write(final)
                proc.stdin.close()
                codigo = proc.wait()
            except BaseException:
                proc.kill()
                proc.wait()
                raise
        if codigo:
            raise RuntimeError((tmp / "ffmpeg.log").read_text())

def enviar_drive(saida, numero, lote):
    nome = f"jogo_{numero:03d}_{modelo_do_video(numero)['nome']}"
    destino = f"destino:saida/Juh-Quiz-7-Erros/{lote}"
    for ext in ("mp4", "txt"):
        arquivo = saida / f"{nome}.{ext}"
        subprocess.run(["rclone", "copyto", str(arquivo), f"{destino}/{arquivo.name}",
                        "--retries", "3"], check=True)
    subprocess.run(["rclone", "check", str(saida), destino, "--include", f"{nome}.mp4",
                    "--include", f"{nome}.txt", "--one-way"], check=True)
    print(f"Conferidos no Drive: {nome}.mp4 e TXT", flush=True)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dados", type=Path, default=BASE / "dados_7_erros.json")
    p.add_argument("--saida", type=Path, default=BASE / "saida")
    p.add_argument("--tempo", type=int, default=20)
    p.add_argument("--revelacao", type=int, default=5)
    p.add_argument("--inicio", type=int, default=1, help="Primeiro número, mantém o ciclo entre lotes")
    p.add_argument("--limite", type=int)
    p.add_argument("--quantidade", type=int, help="Quantidade a partir da posição --inicio no JSON")
    p.add_argument("--lote", default="local")
    p.add_argument("--enviar-drive", action="store_true")
    p.add_argument("--previas", action="store_true")
    a = p.parse_args()
    if not 3 <= a.tempo <= 59 or not 1 <= a.revelacao <= 30 or a.inicio < 1:
        p.error("Tempo: 3–59; revelação: 1–30; início: pelo menos 1.")
    if a.limite is not None and a.limite < 1:
        p.error("Limite deve ser positivo.")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", a.lote):
        p.error("Lote deve conter apenas letras, números, hífen e sublinhado.")
    if a.enviar_drive and a.previas:
        p.error("Prévias não são enviadas como vídeos ao Drive.")
    if a.enviar_drive and not shutil.which("rclone"):
        p.error("Instale rclone para enviar ao Drive.")
    if not a.previas and not shutil.which("ffmpeg"):
        p.error("Instale o FFmpeg ou rode pelo GitHub Actions.")
    itens = json.loads(a.dados.read_text(encoding="utf-8"))
    if not isinstance(itens, list) or not itens:
        p.error("O JSON deve conter uma lista com pelo menos um desafio.")
    if a.quantidade is not None:
        if a.quantidade < 1 or a.inicio+a.quantidade-1 > len(itens):
            p.error(f"Selecione um intervalo de desafios entre 1 e {len(itens)}.")
        itens = itens[a.inicio-1:a.inicio-1+a.quantidade]
    elif a.limite:
        itens = itens[:a.limite]
    for item in itens:
        validar(item)
    if a.enviar_drive:
        subprocess.run(["rclone", "lsf", "destino:", "--max-depth", "1"], check=True)
    a.saida.mkdir(parents=True, exist_ok=True)
    for i, item in enumerate(itens, a.inicio):
        print(f"Gerando vídeo {i}: modelo {modelo_do_video(i)['nome']}", flush=True)
        gerar_video(item, i, a.saida, a.tempo, a.revelacao, a.previas)
        if a.enviar_drive:
            enviar_drive(a.saida, i, a.lote)
    print(f"Pronto: {a.saida.resolve()}")

if __name__ == "__main__":
    main()
