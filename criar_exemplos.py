"""Cria três cenas vetoriais de teste com exatamente sete alterações isoladas."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent

def cena(variante, alterada):
    im = Image.new("RGB", (1000, 580), ["#ffe6cc", "#e4f3f3", "#f0e5fa"][variante])
    d = ImageDraw.Draw(im)
    d.rectangle((0, 435, 1000, 580), fill="#bc865d")
    for x in range(0, 1000, 125):
        d.line((x, 440, x, 580), fill="#d4a680", width=3)
    d.rounded_rectangle((150, 468, 855, 570), 45, fill="#faf0ce")
    d.rectangle((30, 30, 250, 310), fill="#fff8ec", outline="#a47855", width=8)
    d.rectangle((44, 44, 236, 295), fill="#8ed6ed")
    d.line((140, 40, 140, 304), fill="white", width=10)
    d.line((40, 175, 240, 175), fill="white", width=10)
    # 1: sol presente/ausente.
    if not alterada:
        d.ellipse((70, 68, 114, 112), fill="#ffd635")
    d.rectangle((343, 45, 547, 198), fill="#aa774c")
    d.rectangle((355, 57, 535, 186), fill="#bcecf9")
    d.polygon([(356, 186), (402, 92), (446, 167), (481, 110), (535, 186)], fill="#65a965")
    # 2: estrela no quadro muda de cor.
    d.regular_polygon((490, 87, 17), 5, fill="#ff3f81" if alterada else "#ffe234")
    d.ellipse((602, 51, 706, 155), fill="white", outline="#78543e", width=6)
    d.line((654, 103, 654, 68), fill="#483a34", width=5)
    # 3: ponteiro do relógio.
    d.line((654, 103, 684 if alterada else 626, 120 if alterada else 85), fill="#483a34", width=5)
    d.line((834, 197, 834, 438), fill="#76513c", width=12)
    d.ellipse((791, 425, 881, 449), fill="#76513c")
    # 4: abajur amarelo/azul.
    d.polygon([(783, 83), (885, 83), (913, 196), (755, 196)], fill="#6b9eed" if alterada else "#ffe09b")
    d.rounded_rectangle((251, 239, 745, 421), 35, fill=["#64ac99", "#ad8dcc", "#ef9da7"][variante], outline="#557d70", width=5)
    d.rounded_rectangle((213, 326, 780, 465), 25, fill="#78bfa8", outline="#557d70", width=5)
    for x in (246, 714):
        d.rectangle((x, 461, x+20, 489), fill="#704b38")
    # 5: almofada rosa/amarela.
    d.rounded_rectangle((277, 268, 388, 363), 18, fill="#ffcd38" if alterada else "#f26a99")
    # Gato constante.
    d.ellipse((456, 317, 616, 391), fill="#f3a235", outline="#c87b21", width=4)
    d.polygon([(574, 321), (576, 285), (601, 312)], fill="#f3a235")
    d.polygon([(617, 315), (643, 287), (646, 332)], fill="#f3a235")
    d.ellipse((566, 304, 651, 380), fill="#f3a235", outline="#c87b21", width=3)
    d.arc((580, 327, 603, 345), 0, 180, fill="#5b4129", width=3)
    d.arc((615, 327, 638, 345), 0, 180, fill="#5b4129", width=3)
    d.polygon([(604, 350), (616, 350), (610, 358)], fill="#a83e51")
    for y in (337, 352, 367):
        d.line((477, y, 500, y+5), fill="#c87b21", width=5)
    d.rectangle((362, 466, 375, 547), fill="#784c32")
    d.rectangle((625, 466, 638, 547), fill="#784c32")
    d.ellipse((308, 426, 690, 493), fill="#d6a66b", outline="#986743", width=4)
    d.rectangle((536, 445, 641, 460), fill="#8574c7")
    # 6: livro superior vermelho/azul.
    d.rectangle((546, 429, 632, 444), fill="#44a7e2" if alterada else "#e95c69")
    d.arc((456, 423, 493, 464), 260, 90, fill="white", width=6)
    d.rounded_rectangle((418, 424, 467, 470), 6, fill="white")
    # 7: símbolo da caneca quadrado/coração.
    if alterada:
        d.rectangle((431, 437, 454, 458), fill="#f05178")
    else:
        d.ellipse((428, 435, 445, 450), fill="#f05178")
        d.ellipse((441, 435, 458, 450), fill="#f05178")
        d.polygon([(429, 443), (457, 443), (443, 462)], fill="#f05178")
    d.polygon([(65, 390), (151, 390), (138, 467), (79, 467)], fill="#f9f5ee")
    for x, y in [(53, 331), (88, 290), (114, 313), (133, 345)]:
        d.line((108, 394, x+18, y+24), fill="#318749", width=5)
        d.ellipse((x, y, x+44, y+53), fill="#52a45b")
    return im

def main():
    pasta = BASE / "imagens"
    pasta.mkdir(exist_ok=True)
    pontos = [(92, 90, "Sol da janela desapareceu"),
              (490, 87, "Cor da estrela no quadro"),
              (654, 103, "Posição do ponteiro do relógio"),
              (834, 141, "Cor da cúpula do abajur"),
              (332, 315, "Cor da almofada"),
              (589, 437, "Cor do livro superior"),
              (443, 447, "Símbolo da caneca")]
    itens = []
    for i in range(3):
        for letra in "ab":
            cena(i, letra == "b").save(pasta / f"sala_{i+1}_{letra}.png")
        itens.append(dict(titulo=f"Sala do gatinho {i+1}",
                          imagem_a=f"imagens/sala_{i+1}_a.png", imagem_b=f"imagens/sala_{i+1}_b.png",
                          legenda="Encontre os 7 erros na sala do gatinho! Você conseguiu todos? Conte nos comentários.",
                          erros=[dict(x=x/1000, y=y/580, raio=.058, descricao=t) for x,y,t in pontos]))
    (BASE / "dados_7_erros.json").write_text(json.dumps(itens, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
