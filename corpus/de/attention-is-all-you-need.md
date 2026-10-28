---
title: Attention Is All You Need
url: https://de.wikipedia.org/wiki/Attention_Is_All_You_Need
updated: '2026-07-19T14:06:05Z'
language: de
revision: '268945412'
license: CC BY-SA 4.0
source: Wikipedia
---

Attention Is All You Need ist eine 2017 veröffentlichte einflussreiche wissenschaftliche Arbeit im Bereich des maschinellen Lernens von Forschern von Google Research und Google Brain. Die Publikation führte die Transformer-Architektur ein, welche heute die Grundlage vieler Modelle der natürlichen Sprachverarbeitung bildet, insbesondere großer Large Language Model. Die Arbeit wurde über 150'000-mal zitiert und gehört damit zu den am häufigsten zitierten wissenschaftlichen Publikationen des 21. Jahrhunderts.
Der in der Arbeit eingeführte Transformer unterscheidet sich von den modernen Transformern der Large Language Models dadurch, dass er eine Encoder-Decoder-Architektur verwendet, während heutige Sprachmodelle häufig als Decoder-only-Architekturen umgesetzt sind. Der Transformer ist ein neuronales Sequenz-zu-Sequenz-Modell, das auf dem 2014 eingeführten Attention-Mechanismus basiert. Frühere Modelle basierten auf rekurrenten (RNN) oder konvolutionellen Strukturen (CNN), während der Transformer ohne solche Mechanismen auskommt.

## Attention Is All You Need

Die Publikation wurde 2017 auf der NeurIPS-Konferenz veröffentlicht und gilt als ein zentraler Meilenstein im Bereich des Deep Learning. Neben der theoretischen Einführung des Modells enthält die Arbeit Ergebnisse empirischer Experimente, die deutliche Verbesserungen in der maschinellen Übersetzung sowie eine erhebliche Reduktion der Trainingszeit gegenüber damaligen Systemen zeigen.
Der Titel "Attention Is All You Need" ist eine Anspielung auf das Lied All You Need Is Love von The Beatles.

### Autoren

Die Autoren der Arbeit sind Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan Gomez, Łukasz Kaiser und Illia Polosukhin. Alle acht Autoren gelten laut Publikation als gleichberechtigte Hauptbeitragende. Nach Veröffentlichung der Arbeit verließen mehrere der Autoren Google und wechselten zu anderen Unternehmen oder gründeten eigene Start-ups, darunter OpenAI und Anthropic.

### Hintergrund und Inhalt

Vor der Einführung des Transformers basierten Sequenzmodelle überwiegend auf rekurrenten oder konvolutionellen neuronalen Netzen in Encoder-Decoder-Architekturen. Diese verarbeiten Sequenzen schrittweise, wodurch die Parallelisierbarkeit eingeschränkt ist und das Training auf moderner Hardware vergleichsweise langsam erfolgt.
Mit dem Transformer wurde diese sequentielle Verarbeitung vollständig durch eine Attention-basierte Architektur ersetzt, die ohne Rekurrenz oder Faltung auskommt und Eingabesequenzen parallel verarbeiten kann. Dadurch ergeben sich deutlich effizientere Trainingsverfahren und eine bessere Skalierbarkeit auf großen Datensätzen.
Der Ansatz beruht auf der Idee, dass sogenannte Self-Attention ausreicht, um Abhängigkeiten innerhalb von Sequenzen zu modellieren. Der Attention-Mechanismus wurde bereits zuvor eingesetzt, jedoch lediglich als Ergänzung bestehender Architekturen und nicht als alleinige Grundlage des Modells.

### Bedeutung und Einfluss

Insgesamt etablierte die Arbeit eine neue Architekturklasse, die sich schnell zum Standard in der natürlichen Sprachverarbeitung entwickelte und in zahlreichen Folgearbeiten weiter ausgebaut wurde.
Die Transformer-Architektur bildet die Grundlage nahezu aller modernen Large Language Models wie ChatGPT und Gemini sowie vieler moderner Modelle der Bildverarbeitung.

## Architektur des ursprünglichen Transformer

Der Hauptteil der Publikation ist die Erklärung der Transformer-Architektur. Dabei werden die einzelnen Komponenten (Encoder/Decoder) sowie deren Unterstrukturen erläutert.

### Übersicht über die Architektur des Transformers

Die Transformer-Architektur besteht aus einer Encoder-Decoder-Architektur und lässt sich grob wie folgt zusammenfassen (wichtige Zwischenschritte sind dabei ausgeblendet):

${\begin{aligned}x\to {\text{Encoder}}\to &z\\\downarrow &\\(y_{<t},&z)\to {\text{Decoder}}\to p(y_{t}\mid y_{<t},x)\end{aligned}}$

### Encoder-Decoder-Architektur

Die Encoder-Decoder-Architektur lässt sich so beschreiben:

Encoder-Komponente: Der Encoder wandelt eine Eingabesequenz 
$x=(x_{1},\dots ,x_{n})$

 aus Tokens in eine kontinuierliche Repräsentation 
$z=(z_{1},\dots ,z_{n})$

 um, wobei jedes 
$z_{i}$

 ein Vektor ist.
Decoder-Komponente: Der Decoder erhält als Input die vom Encoder erzeugte Repräsentation 
$z$

 sowie die bisher erzeugten Ausgabesymbole 
$y_{<t}:=(y_{0},y_{1},\dots ,y_{t-1})$

 bis zum Zeitpunkt 
$t$

. Im ersten Schritt 
$t=1$

 gilt 
$y_{<t}:=(y_{0})$

 wobei 
$y_{0}:={\text{START}}$

 ein Startsymbol ist. Der Decoder gibt als Ausgabe eine bedingte Wahrscheinlichkeitsverteilung 
$p(y_{t}\mid y_{<t},x)$

 über das nächste Ausgabesymbol 
$y_{t}$

 zurück.
Die Eingaben 
$x$

 und 
$y_{<t}$

 werden zu Beginn durch eine Einbettungs-Funktion 
$h$

 in einen hochdimensionalen Raum eingebettet. Der Transformer lässt sich dann kompakt wie folgt verstehen:

${\text{Transformer}}(x,y_{<t})={\text{Decoder}}({\text{Encoder}}(h(x)),h(y_{<t}))=p(y_{t}\mid y_{<t},x).$

#### Schichten des Encoders und Decoders

Encoder und Decoder bestehen jeweils aus gestapelten Schichten mit identischer Struktur. Sowohl der Encoder als auch der Decoder bestehen aus 
$N$

 identischen Schichten (im Original 
$N=6$

):

${\text{Encoder}}(x)={\text{S}}_{E}^{(N)}\circ \cdots \circ {\text{S}}_{E}^{(1)}(h(x)),\qquad {\text{Decoder}}(y_{<t},z)={\text{S}}_{D}^{(N)}\circ \cdots \circ {\text{S}}_{D}^{(1)}(h(y_{<t}),z)$

Eine Encoder-Schicht besteht wiederum aus zwei aufeinanderfolgenden Teilschichten 
${\text{SubLayer}}$

, eine Decoder-Schicht hingegen aus drei aufeinanderfolgenden Teilschichten.

#### Teilschichten des Encoders und Decoders

Die Teilschichten 
${\text{SubLayer}}\in \{{\text{MHA}},{\text{FFN}}\}$

 des Encoders sind

Multi-Head Self-Attention 
${\text{MHA}}$

position-wise Feedforward neural network 
${\text{FFN}}$

.
Die Teilschichten 
${\text{SubLayer}}\in \{{\text{MaskedMHA}},{\text{EncDecAtt}},{\text{FFN}}\}$

 des Decoder sind

Masked Multi-Head Self-Attention 
${\text{MaskedMHA}}$

Encoder-Decoder-Attention 
${\text{EncDecAtt}}$

position-wise Feedforward Neural Network 
${\text{FFN}}.$

Jede Teilschicht ist zudem mit einer Residual-Verbindung und anschließender Normalisierung versehen, das heißt, man addiert den Eingang zur Ausgabe der Teilschicht und normalisiert das Ergebnis:

${\text{LayerNorm}}(x+{\text{SubLayer}}(x)).$

Es ist zu beachten, dass zwei Schichten innerhalb des Encoders respektive des Decoders denselben Aufbau besitzen, die einzelnen Teilschichten jeweils aber eigene Parameter haben.

##### Layer-Normalisierung

Die Layer-Normalisierung ist im Kern die aus der Statistik bekannte Standardisierung. Sei 
$s=(s_{1},\dots ,s_{t})$

 der Eingabevektor in 
${\text{LayerNorm}}(s)$

, dann werden die einzelnen Komponenten von 
$s$

 mithilfe des empirischen Mittelwerts und der empirischen Varianz standardisiert:

${\widehat {s_{i}}}={\frac {s_{i}-\mu }{\sigma }},\qquad \mu ={\frac {1}{t}}\sum _{i=1}^{t}s_{i},\qquad \sigma ={\sqrt {{\frac {1}{t}}\sum _{i=1}^{t}(s_{i}-\mu )^{2}}}$

Auf das Resultat wird dann eine affine Transformation 
$s\mapsto as+b$

 angewendet:

$f_{i}({\widehat {s_{i}}})=g_{i}{\widehat {s_{i}}}+b_{i},$

wobei der Skalierungsvektor 
$g=(g_{1},\dots ,g_{t})$

 und der Verschiebungsvektor 
$b=(b_{1},\dots ,b_{t})$

 im Training gelernt werden.
Es gilt dann

${\text{LayerNorm}}(s)=(f_{1}({\widehat {s_{1}}}),\,\dots ,\,f_{t}({\widehat {s_{t}}}))=(g_{1}{\widehat {s_{1}}}+b_{1},\,\dots ,\,g_{t}{\widehat {s_{t}}}+b_{t}).$

### Einbettung mit Positional Encoding

Bevor die Eingabesequenzen 
$x=(x_{1},\dots ,x_{n})$

 im Encoder und 
$y_{<t}$

 im Decoder in das Modell eingegeben werden, werden die Eingaben zunächst in einen hochdimensionalen Vektorraum eingebettet und mit Informationen zur Position ergänzt:

$x_{i}\mapsto {\text{Embedding}}(x_{i})+{\text{PE}}(i)$

Da der Transformer keine rekurrente oder konvolutionelle Struktur besitzt, wird die Positionsinformation durch ein Positional Encoding ergänzt, das jeder Position 
$i$

 einen Vektor

${\text{PE}}(i)=({\text{PE}}(i,0),\,{\text{PE}}(i,1),\,\dots ,\,{\text{PE}}(i,d_{\text{model}}-1))\in \mathbb {R} ^{d_{\text{model}}}$

zuordnet. Die 
$k$

-te Komponente des Positional-Encoding-Vektors ist definiert durch:

${\text{PE}}(i,2k)=\sin \left({\frac {i}{10000^{2k/d_{\text{model}}}}}\right),\qquad {\text{PE}}(i,2k+1)=\cos \left({\frac {i}{10000^{2k/d_{\text{model}}}}}\right)$

wobei 
$i$

 der Positionsindex in der Sequenz 
$x$

.
Die kombinierte Einbettung ist dann definiert als die Matrix 
$h(x)\in \mathbb {R} ^{n\times d_{\text{model}}}$

, definiert als 
$h(x)=[h_{1}(x),\dots ,h_{n}(x)]^{T}$

 mit

$h_{i}(x):=\operatorname {Embedding} (x_{i})+{\text{PE}}(i)$

,
wobei 
$i$

 der Positionsindex in der Sequenz 
$x$

 ist.
Als Veranschaulichung sei die Eingabesequenz 
$x=({\text{Der}},{\text{Hund}},{\text{bellt}},\dots )$

. Für das zweite Token 
$x_{2}={\text{Hund}}$

 könnte die Einbettung und das Positional-Encoding beispielsweise wie folgt aussehen:

$h_{2}(x)={\text{Embedding}}(x_{2})+{\text{PE}}(2)=(0.2,\,-0.4,\,0.7,\dots )+(0.91,\,-0.42,\,0.02,\dots ).$

### Encoder

Jede Encoder-Schicht besteht aus zwei Teilschichten:

Multi-Head Self-Attention 
${\text{MHA}}$

: ein Attentionmechanismus, bei dem Query, Key und Value aus derselben Eingabesequenz stammen, sodass für jedes Token Information aller Token der Sequenz entsprechend ihrer Relevanz kombiniert werden.
position-wise Feedforward neural network 
${\text{FFN}}$

: Ein Feedforward-Netzwerk, das für jedes Token der Sequenz separat und mit denselben Parametern eine nichtlineare Transformation seiner Repräsentation durchführt, ohne Informationen zwischen den Tokens auszutauschen
Mit Layer-Normalisierung hat man

${\begin{aligned}{\text{S}}_{\text{MHA}}^{E}(x)&:={\text{LayerNorm}}(x+{\text{MHA}}(x))\\{\text{S}}_{\text{FFN}}^{E}(x)&:={\text{LayerNorm}}(x+{\text{FFN}}(x))\end{aligned}}$

Die 
$i$

-te Encoder-Schicht ist dann definiert als

${\text{S}}^{E,(i)}(x):={\text{S}}_{\text{FFN}}^{E,(i)}\left({\text{S}}_{\text{MHA}}^{E,(i)}(x)\right)$

Der Encoder ist die Verkettung dieser Schichten:

${\text{Encoder}}(x)={\text{S}}^{E,(N)}\circ \cdots \circ {\text{S}}^{E,(1)}(x)$

### Decoder

Jede Decoder-Schicht besteht aus:

Masked Multi-Head Self-Attention 
${\text{MaskedMHA}}$

: Eine Variante der Multi-Head Self-Attention, bei der eine Maskierung verhindert, dass eine Position auf zukünftige Positionen zugreifen kann, wodurch die autoregressive Struktur erhalten bleibt
Encoder-Decoder-Attention 
${\text{EncDecAtt}}$

: Ein Attention-Mechanismus, bei dem die Keys und Values aus der Ausgabe des Encoders stammen und die Queries aus dem Decoder, sodass der Decoder auf die kodierte Eingabesequenz zugreifen kann.
Position-wise Feedforward Neural Network 
${\text{FFN}}$

.
Analog zum Encoder werden auch diese Normalisiert

${\begin{aligned}{\text{S}}_{\text{MaskedMHA}}^{D}(y)&:={\text{LayerNorm}}(y+{\text{MaskedMHA}}(y))\\{\text{S}}_{\text{EncDecAtt}}^{D}(y,z)&:={\text{LayerNorm}}(y+{\text{EncDecAtt}}(y,z))\\{\text{S}}_{\text{FFN}}^{D}(y)&:={\text{LayerNorm}}(y+{\text{FFN}}(y))\end{aligned}}$

Die 
$i$

-te Decoder-Schicht ist dann definiert als

${\text{S}}^{D,(i)}(y,z):={\text{S}}_{\text{FFN}}^{D,(i)}\left({\text{S}}_{\text{EncDecAtt}}^{D,(i)}\left({\text{S}}_{\text{MaskedMHA}}^{D,(i)}(y),z\right)\right)$

Der Decoder ist die Verkettung dieser Schichten:

${\text{Decoder}}(y_{<t},z)={\text{S}}^{D,(N)}\circ \cdots \circ {\text{S}}^{D,(1)}(y_{<t},z)$

### Position-wise Feedforward-Netzwerk

Jede Schicht enthält ein Feedforward-Netzwerk, das unabhängig auf jede Position angewendet wird und daher als position-wise Feedforward Neural Network bezeichnet wird. Es besteht aus zwei linearen Transformationen und einem Rectifier dazwischen:

${\text{FFN}}(x)=\max(0,xW_{1}+b_{1})W_{2}+b_{2}$

### Attention-Mechanismen

Beim Attention-Mechanismus werden zuerst aus der eingebetteten Eingabesequenz 
$h(x)\in \mathbb {R} ^{n\times d_{\text{model}}}$

 mittels lernbaren Gewichtsmatrizen 
$W^{Q},W^{K},W^{V}$

 lineare Projektionen berechnet, daraus resultieren drei Matrizen, welche als 
$Q$

 („Query“), 
$K$

 („Key“)  und 
$V$

 („Value“) bezeichnet werden:

$Q(x)=h(x)W^{Q}\in \mathbb {R} ^{n\times d_{k}},\quad K(x)=h(x)W^{K}\in \mathbb {R} ^{n\times d_{k}},\quad V(x)=h(x)W^{V}\in \mathbb {R} ^{n\times d_{v}}$

Metaphorisch lassen sich diese wie folgt interpretieren:

$Q$

 beschreibt „was wird gesucht?“,

$K$

 beschreibt „welche Merkmale werden mit der Suche verglichen?“,

$V$

 beschreibt „welche Information wird geliefert?“.
Die tatsächliche Bedeutungen der drei Vektoren wird jedoch erst durch die im Training gelernten Projektionen erzeugt.

Die Attention berechnet Ähnlichkeiten zwischen 
$Q$

 und 
$K$

 via Skalarprodukt und bildet daraus Gewichte 
$\alpha $

, mit Hilfe deren die 
$V$

-Vektoren gewichtet werden.
Man schreibt für die verschiedenen Formen von Attention statt 
${\text{Attention}}(x)$

 häufig 
${\text{Attention}}(Q,K,V)$

, dies ist wie folgt zu verstehen

$x\mapsto h(x)\mapsto (Q(x),\,K(x),\,V(x))\mapsto {\text{Attention}}(Q,K,V)$

#### Self-Attention und Cross-Attention

Man spricht von Self-Attention, wenn 
$Q$

, 
$K$

 und 
$V$

 durch dieselbe Eingabesequenz erzeugt wurden. Man spricht von Cross-Attention, wenn 
$Q$

 aus einer Sequenz kommt und 
$K$

 und 
$V$

 aus einer anderen Sequenz.
Beim Cross-Attention können dann die Sequenzlängen (das heißt Anzahl Tokens) auch unterschiedlich sein 
$n\neq m$
$Q(x)\in \mathbb {R} ^{n\times d_{k}},\quad K(x)\in \mathbb {R} ^{m\times d_{k}},\quad V(x)\in \mathbb {R} ^{m\times d_{v}}.$

#### Attention-Funktion auf einen Query

Für jeden Token gibt es einen Query 
$q\in \mathbb {R} ^{d_{k}}$

. Eine Attention-Funktion bildet einen Query 
$q$

 und eine Menge von Key-Value-Paaren 
$\{(k_{i},v_{i})\}_{i=1}^{n}$

 auf einen mit Softmax gewichteten Vektor ab:

${\text{Attention}}(q,\{(k_{i},v_{i})\}_{i=1}^{n})=\sum _{i=1}^{n}\alpha _{i}v_{i},\qquad \alpha _{i}:={\text{softmax}}_{i}\left({\frac {q\cdot k_{i}}{\sqrt {d_{k}}}}\right)={\frac {\exp(q\cdot k_{i}/{\sqrt {d_{k}}})}{\sum \limits _{j}\exp(q\cdot k_{j}/{\sqrt {d_{k}}})}},\qquad q\cdot k_{i}:=\sum \limits _{l=1}^{d_{k}}q_{l}k_{il},$

das heißt die Skalarprodukte 
$q\cdot k_{i}$

 werden mit 
${\sqrt {d_{k}}}$

 normalisiert (wobei 
$q,k_{i}\in \mathbb {R} ^{d_{k}}$

), um die Gewichte 
$\alpha _{i}$

 zu bilden.

$q\cdot k_{i}$

 misst, wie ähnlich der Query 
$q$

 und der Key 
$k_{i}$

 sind.

${\sqrt {d_{k}}}$

 wird zur Skalierung verwendet, damit die Skalarprodukte bei höherer Dimension stabil bleiben,

$\alpha _{i}$

 gewichtet 
$v_{i}$

 höher, wenn 
$k_{i}$

 sehr ähnlich zu 
$q$

 ist.
Das bedeutet 
$k_{i}$

 bestimmt, wie relevant das zugehörige 
$v_{i}$

 auf den Query 
$q$

 ist.

#### Attention-Funktion auf alle Queries (Self-Attention und Cross-Attention)

Die Attention angewendet auf alle Queries:

${\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{T}}{\sqrt {d_{k}}}}\right)V=AV=O,$

im Falle von Self-Attention sind die Matrizen 
$A=[a_{ij}]\in \mathbb {R} ^{n\times n}$

 und 
$O=[o_{il}]\in \mathbb {R} ^{n\times d_{v}}$

 definiert als

$a_{ij}={\frac {\exp(q_{i}\cdot k_{j}/{\sqrt {d_{k}}})}{\sum \limits _{m=1}^{n}\exp(q_{i}\cdot k_{m}/{\sqrt {d_{k}}})}},\qquad o_{il}=\sum \limits _{j=1}^{n}a_{ij}v_{jl}.$

Im Falle von Cross-Attention gilt 
$A=[a_{ij}]\in \mathbb {R} ^{n\times m}$

 und 
$O=[o_{il}]\in \mathbb {R} ^{n\times d_{v}}$

 definiert als

$a_{ij}={\frac {\exp(q_{i}\cdot k_{j}/{\sqrt {d_{k}}})}{\sum \limits _{s=1}^{m}\exp(q_{i}\cdot k_{s}/{\sqrt {d_{k}}})}},\qquad o_{il}=\sum \limits _{j=1}^{m}a_{ij}v_{jl}.$

#### Verschiedene Formen von Attention

Masked Self-Attention: Im Decoder wird die Attention so eingeschränkt, dass jedes Element der Position 
$i$

 der Sequenz 
$(y_{1},y_{2},\dots ,y_{t})$

 nur seine und die früheren Positionen 
$1,\dots ,i$

 berücksichtigt:

${\text{MaskedMHA}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{T}}{\sqrt {d_{k}}}}+M\right)V$

wobei 
$M$

 die Maskierungs-Matrix ist mit 
$M_{ij}=0$

 für erlaubte und 
$M_{ij}=-\infty $

 für verbotene Positionen.
Encoder-Decoder-Attention: Queries stammen aus dem Decoder, Keys und Values aus dem Encoder:

${\text{EncDecAtt}}(Q,K,V),\quad {\text{mit }}Q{\text{ aus Decoder, }}\quad K{\text{ und }}V{\text{ aus Encoder}}.$

Multi-Head Attention: Berechnet mehrere Attention-Köpfe parallel. Die Eingaben 
$Q,K,V$

 stammen je nach Block aus Self-Attention (alle aus derselben Sequenz) oder aus der Encoder-Decoder-Attention (Query aus dem Decoder, Keys und Values aus dem Encoder):

${\text{MHA}}(Q,K,V)={\text{Concat}}({\text{head}}_{1},\dots ,{\text{head}}_{h})W^{O}$

mit:

${\text{head}}_{i}={\text{Attention}}(QW_{i}^{Q},KW_{i}^{K},VW_{i}^{V})$

.
Die Konkatenation 
${\text{Concat}}$

 ist einfach das Aneinanderfügen von Vektoren, das heißt für zwei Vektor 
$v_{1}={\begin{bmatrix}1\\2\end{bmatrix}}$

 und 
$v_{2}={\begin{bmatrix}3\\4\end{bmatrix}}$

 ist die Operation definiert als

${\text{Concat}}(v_{1},v_{2})={\begin{bmatrix}1\\2\\3\\4\end{bmatrix}}.$

### Ausgabe

Die Wahrscheinlichkeit der gesamten Ausgabesequenz ist

$p(y\mid x)=\prod \limits _{t=1}^{T}p(y_{t}\mid y_{<t},x).$

Die Ausgabe ist nicht mehr Teil der Transformer-Architektur oder der Publikation, doch anschließend wird das nächste Symbol durch

$y_{t}={\underset {y\in V}{\operatorname {arg\,max} }}\;p(y\mid y_{<t},x)$

bestimmt, wobei 
$V$

 die Menge aller möglichen Ausgabesymbole ist.
