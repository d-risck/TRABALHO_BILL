# Pirâmide 3D com Trackball

Trabalho prático de Computação Gráfica em Python: uma pirâmide de base quadrada, iluminada e controlada pelo mouse. Usa GLFW para a janela, OpenGL para desenhar, NumPy para os cálculos e OpenCV para converter cores HSV em RGB.

## Como executar no Windows (PowerShell)

Requer Python 3.11 ou superior e um driver de vídeo com suporte a OpenGL 2.1.
Execute os comandos na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\main.py
```

Não é necessário ativar o ambiente virtual. Para as próximas execuções, basta o último comando. Se a janela não abrir, confira a mensagem no terminal e o driver da placa de vídeo.

## Controles

| Controle | Ação |
| --- | --- |
| Botão esquerdo + arraste | Gira a pirâmide com Trackball |
| Roda do mouse | Aproxima ou afasta a câmera |
| W / S / A / D | Move o objeto para cima / baixo / esquerda / direita |
| + / - | Aumenta / diminui o objeto (a tecla = também aumenta) |
| C | Alterna as cores, mudando a matiz em HSV |
| L | Liga ou desliga a iluminação |
| R | Restaura a posição, orientação, câmera, escala e cores iniciais |
| Esc | Fecha a janela |

## Organização

```text
src/
  main.py          Janela, interação, matrizes e renderização
  geometria.py     Vértices, faces, normais e cores
  trackball.py     Mapeamento do mouse e operações com quatérnios
tests/
  test_matematica.py
  test_interacao.py
requirements.txt
.gitignore
README.md
```

O ambiente `.venv/`, arquivos de cache e a captura de verificação são ignorados pelo Git. O repositório local já está inicializado; para registrar a entrega, depois de revisar os arquivos:

```powershell
git add .
git commit -m "Implementa piramide 3D com iluminacao e trackball"
```

Publicar no GitHub exige criar um repositório na sua conta e configurar o remoto; o projeto funciona localmente sem essa publicação.

## Como o código atende às quatro partes

### 1. Ambiente e malha

A pirâmide possui **5 vértices e 5 faces**: quatro laterais triangulares e uma base quadrada. `VERTICES` guarda as posições e `FACES` guarda os índices de cada face. O desenho usa `GL_TRIANGLES` nas laterais e `GL_QUADS` na base, com uma única cor e uma única normal para toda a base.

Os quatro lados da base medem 2 unidades, têm ângulos retos e estão no plano y = −1. Em perspectiva, o quadrado pode parecer um losango ou trapézio; sua geometria continua quadrada. Usar dois triângulos coplanares também seria correto, mas a face de quatro vértices deixa a estrutura mais direta para explicar.

GLFW cria a janela e o contexto OpenGL 2.1. `GL_DEPTH_TEST` usa o buffer de profundidade para que uma superfície próxima esconda outra distante. O pipeline clássico foi escolhido para deixar as operações do enunciado visíveis, sem adicionar shaders ao trabalho.

### 2. Espaços e transformações

Em `desenhar`, o código monta explicitamente **M = T · R · S**. Para um vértice representado como vetor coluna, a escala é aplicada primeiro, depois a rotação e depois a translação. A ordem importa: girar antes de transladar mantém a rotação em torno do centro local do objeto.

`gluLookAt` define a matriz de visão: a câmera está no eixo Z e olha para a origem. A roda do mouse modifica sua distância. `gluPerspective` define a perspectiva com campo de visão de 45°, proporção da janela e planos próximo/distante de 0,1 e 100.

O caminho completo é **local → mundo → câmera → projeção → tela**, expresso por `P · V · M · vértice`. O OpenGL realiza a divisão pela coordenada homogênea e o mapeamento para o viewport. A transposição de `modelo` adapta o armazenamento do NumPy à ordem por colunas esperada pelo OpenGL.

### 3. Normais, iluminação e OpenCV

Cada normal é calculada por **N = (V1 − V0) × (V2 − V0)** e dividida pelo próprio comprimento. A ordem dos vértices faz as normais apontarem para fora. Cada face recebe sua normal por `glNormal3fv`.

A iluminação tem uma componente ambiente e uma componente difusa. A difusa depende do alinhamento entre a normal e a direção da luz: faces voltadas para a luz ficam mais claras. `GL_NORMALIZE` mantém as normais unitárias depois da transformação e `GL_FLAT` evidencia as faces planas. A posição da luz é definida após a visão e antes do modelo, ficando fixa no mundo quando o objeto gira.

As cores são definidas em **HSV**: H controla a matiz, S a saturação e V o brilho. No OpenCV com `uint8`, H vai de 0 a 179 e S/V de 0 a 255. `cv2.cvtColor(..., COLOR_HSV2RGB)` converte as cores para **RGB**, e o código divide por 255 para fornecer valores entre 0 e 1 ao OpenGL. A tecla C altera H; a tecla L permite observar a diferença entre a cor base e a cor iluminada.

### 4. Trackball e quatérnios

1. O clique inicia o arraste; cada movimento captura uma nova posição do cursor.
2. `mapear_mouse` centraliza as coordenadas e inverte Y. Dentro do círculo virtual, calcula **z = √(1 − x² − y²)**; fora, projeta o ponto na borda com z = 0. A menor dimensão da janela mantém o círculo sem distorção.
3. `quat_arraste` calcula o eixo com **início × fim** e o ângulo com **arccos(início · fim)**. Os dois vetores são unitários, e o produto escalar é limitado a [−1, 1] para evitar erros numéricos.
4. O quatérnio é **q = (cos(θ/2), eixo · sin(θ/2))**, com componentes na ordem `(w, x, y, z)`.
5. O produto de Hamilton acumula **q_atual = q_delta × q_atual**. O novo giro acontece nos eixos da tela, pois a câmera está alinhada com os eixos do mundo. O resultado é normalizado para evitar deriva numérica.
6. `matriz_rotacao` converte a orientação em uma matriz 4 × 4, usada em M e enviada ao OpenGL a cada quadro.

Quatérnios representam a orientação sem acumular três ângulos de Euler, evitando a trava de cardã. Movimentos nulos e vetores opostos também têm tratamento explícito.

## Verificação

Testes dos conceitos matemáticos, sem abrir janela:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Verificação do contexto OpenGL e de um quadro renderizado (salva `demonstracao.png` e encerra):

```powershell
.\.venv\Scripts\python.exe src\main.py --verificar
```

Os testes verificam normais unitárias, perpendiculares e externas, mapeamento na hemisfera, rotações entre vetores, composição e estabilidade dos quatérnios e cores RGB válidas. Também verificam os callbacks de clique, arraste, soltura, teclas e zoom com entradas simuladas. A captura verifica a renderização; para confirmar a interação completa, execute normalmente e use os controles.

## Roteiro curto para apresentar

1. Mostre `VERTICES` e `FACES`: “A pirâmide é uma lista de pontos e de faces: quatro triângulos nas laterais e um quadrado na base.”
2. Gire com o mouse: “Mapeio o cursor para uma esfera virtual e acumulo a orientação com quatérnios.”
3. Use WASD, +/− e a roda: “Aqui demonstro translação, escala e mudança da posição da câmera.”
4. Desligue e ligue a luz com L: “As normais calculadas pelo produto vetorial determinam a intensidade da iluminação.”
5. Troque as cores com C: “Defino as cores em HSV e uso OpenCV para convertê-las para RGB.”
6. Pressione R para restaurar a cena e Esc para fechar.

Antes da apresentação, teste também na máquina da sala, pois a criação do contexto depende do driver gráfico instalado.
