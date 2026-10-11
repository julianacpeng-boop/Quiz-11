# JUH QUIZ — Jogo dos 7 erros

Os modelos alternam automaticamente: 1 rosa, 2 azul, 3 roxo, 4 rosa, 5 azul, 6 roxo…
Cada vídeo usa um desafio inteiro. Não troca de modelo durante o mesmo vídeo.

## Mais fácil no celular: Colab com Meu Drive

1. Abra https://colab.research.google.com/ e envie `Juh_Quiz_7_Erros_Drive.ipynb`.
2. Execute as células e autorize o acesso ao seu Google Drive.
3. Os vídeos e TXT serão gravados em `Meu Drive/JUH QUIZ - Jogo dos 7 Erros/Videos`.

O notebook é independente: inclui o código, a fonte e três desafios de exemplo.
Para novos desafios, troque as imagens e o JSON na pasta `Codigo` criada no Drive.
Ao rodar novamente, o notebook preserva esse código e esses dados. Edite `INICIO`
para continuar a numeração de um novo lote. Por exemplo: após 3 vídeos, use 4.
Não reutilize o mesmo número se quiser preservar as saídas anteriores.

## GitHub Actions

Crie um repositório separado e envie o conteúdo desta pasta na raiz, incluindo
`.github/workflows/gerar.yml`. O gerador é independente do seu Quiz-10.
Em Actions, escolha **Gerar jogo dos 7 erros → Run workflow**.
Ao terminar, baixe o artefato `Juh-Quiz-7-Erros`.

Para salvar no Drive pelo GitHub, use o mesmo método do Quiz-10:
Settings → Secrets and variables → Actions → New repository secret.
Nome: `RCLONE_DRIVE_TOKEN`. Valor: o JSON completo da autorização já usada no
Quiz-10. Se o novo repositório não tiver esse Secret, cadastre a cópia original.
O GitHub não permite revelar o valor antigo; sem essa cópia, refaça a autorização.
Não coloque o token em arquivos nem em conversas.

Não precisa de conta de serviço nem Drive compartilhado. A pasta raiz é a mesma
configurada no workflow atual do Quiz-10: `1IeWfSGxVOgY4nwLQwGxzPZMqRCO81i8B`.
As saídas vão para `saida/Juh-Quiz-7-Erros/execucao-NUMERO/`, separadas do Quiz-10.
Abra Actions → Gerar 7 erros e salvar no Drive → Run workflow. Início 1 e
quantidade 1 para um teste; quantidade 3 para todos os exemplos incluídos.
O envio e a conferência ocorrem após cada vídeo, junto com seu TXT.
O acesso real só poderá ser confirmado ao rodar com seu Secret no GitHub.

## Saídas de cada desafio

- MP4 vertical 1080 × 1920, 30 fps, 20 segundos para encontrar e 5 de resposta.
- PNG da capa e PNG com a resposta circulada.
- TXT da legenda, com o mesmo nome do MP4, UTF-8 e quatro hashtags.
- TXT separado do gabarito (não é legenda).
- Toques de contagem e sinal na revelação. Esta versão não contém narração.

O arquivo de legenda usa:

```text
CAPA_SEGUNDOS=2

Encontre os 7 erros na sala do gatinho! Você conseguiu todos? Conte nos comentários.
#JuhQuiz #7Erros #DesafioVisual #Kwai
```

`CAPA_SEGUNDOS` é instrução para seu publicador, não faz parte da legenda pública.

## Novos jogos / imagens detalhadas

Os três desafios incluídos usam ilustrações simples de teste, criadas por código.
O layout segue as cores, cards brancos e duas cenas empilhadas das sugestões,
mas não usa as ilustrações geradas das prévias, que não tinham sete erros validados.
Você pode usar qualquer par de imagens detalhadas com sete diferenças confirmadas.

Coloque os pares em `imagens/` e cadastre cada um em `dados_7_erros.json`.
As duas imagens devem ter o mesmo tamanho e enquadramento. Não são cortadas.
Cada erro tem `x`, `y` e `raio` proporcionais: x é fração da largura, y da altura
e raio é fração do menor lado. Exemplo: x=0.5, y=0.5 marca o centro.
As posições devem corresponder nos dois quadros. O script valida sete marcações,
mas a confirmação visual de sete diferenças em imagens externas é sua.
O campo `legenda` é individual por vídeo. O campo `titulo` identifica o desafio.

## Rodar no computador

Instale Python, FFmpeg e `pip install -r requirements.txt`.

```bash
python gerar_7_erros.py
python gerar_7_erros.py --previas
python gerar_7_erros.py --inicio 4 --tempo 20 --revelacao 5
```

`criar_exemplos.py` recria os exemplos e sobrescreve o JSON: não execute depois
de personalizar seus desafios. As saídas de nomes iguais também são substituídas.
