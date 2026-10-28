---
title: Transformer (Maschinelles Lernen)
url: https://de.wikipedia.org/wiki/Transformer_(Maschinelles_Lernen)
updated: '2026-05-03T11:44:56Z'
language: de
revision: '266701409'
license: CC BY-SA 4.0
source: Wikipedia
---

Ein Transformer ist eine von Google weiterentwickelte Deep Learning (DL)-Architektur, die einen sogenannten „Aufmerksamkeitsmechanismus“ (englisch attention) als Teil anderer Algorithmusartefakte einsetzt. Das Konzept wurde 2017 vorgestellt und ist Teil der Grundstruktur des generativen vortrainierten Transformers (GPT), auch bekannt als Large Language Models (LLM), sowie anderer vortrainierter Modelle. Letztere sind Modelle, die mithilfe eines großen Datensatzes trainiert wurden, um später für eine bestimmte Aufgabe eingesetzt zu werden.
Im Anwendungsfall der maschinellen Übersetzung, wird Text durch Worteinbettung (Embedding) in numerische Darstellungen in Form von Vektoren umgewandelt und statistisch weiterverarbeitet. Dies kann z. B. dazu benutzt werden, Text von einer Sprache in eine andere zu übersetzen. Dazu wird ein Transformer mittels maschinellem Lernen (ML) anhand einer (großen) Menge von Beispieltexten trainiert, bevor das trainierte Modell dann zur Übersetzung verwendet werden kann. Weitere Beispielanwendungen von Transformer-Architekturen sind die Textgenerierung oder die Zusammenfassung längerer Texte. Transformer haben sich als effizienter als Long Short-Term Memory-Architekturen (LSTM) erwiesen. Letztere Architektur (LSTM) wird beispielsweise von Google Translate seit c. 2016 eingesetzt, eine Adaption der Neural Machine Translation (NMT) durch Google (GNMT). Der Fokus des restlichen Artikels liegt jedoch auf dem Prinzip der Transformer.

## Hintergrund

Transformer wurden 2017 im Rahmen der Neural Information Processing Systems-Konferenz (NeuIPS) von Google-Mitarbeitern vorgestellt und wenig später in der Arbeit Attention Is All You Need veröffentlicht. Die ersten Forschungen zu der Transformer-Technik (sogenannte „fast weight programmers“) gehen jedoch bis in die 1990er Jahre unter Jürgen Schmidhuber zurück.
Bei der Verarbeitung natürlicher Sprache (NLP) wurden vor der Einführung des Transformers rekurrente Modelle (RNN) wie Long Short-Term Memory (LSTM), GRU und Seq2Seq eingesetzt, welche eine Eingangssequenz sequenziell abarbeiten. Diese Methoden wurden später um einen Aufmerksamkeitsmechanismus erweitert.
Man spricht als Teil der Transformer auch von dem „Aufmerksamkeitsmechanismus“ (englisch attention). Sie wurden bereits 2015 im Kontext der maschinellen Übersetzung verwendet. Während sie immer noch auf einem rekurrenten neuronalen Netz (RNN) basierten, entfernte der 2017 Ansatz von Google den RNN-Anteil und reduzierten den Transformer nur auf „Selbst-Aufmerksamkeit“ (englisch self-attention). Diese neue Architektur (Transformer) übertraf vorherige Konzepte. Der Google-Transformer verzichtete somit auf die rekurrente Struktur (RNN) sowie Convolutional Neural Network (CNN) und basierte stattdessen nur auf dem Selbst-Aufmerksamkeitsmechanismus, kombiniert mit Feed-Forward Netzen (FFN), vgl. das Blockdiagramm weiter unten.
Das Konzept des Transformer soll menschliche kognitive Aufmerksamkeit mathematisch nachahmen und die wesentlichen Sinnzusammenhänge in einem gegebenen Kontext erkennen. Der Algorithmus berechnet eine „weiche“ Gewichtung für jedes Wort, genauer gesagt für die Einbettung in seinem aktuellen Kontextfenster. Diese Gewichte können berechnet werden:

parallel (z. B. in Transformern)
sequentiell (z. B. in RNNs).
„Weiche“ Gewichte können sich im Gegensatz zu (vor)trainierten „harten“ Gewichten, die fix sind und keine Anpassung an wechselnden Kontext erlauben, bei jedem Durchlauf ändern. Sie erzielen bei reduziertem Rechenaufwand ähnliche oder bessere Ergebnisse bei der Transformation von Sequenzen als sequenziell-arbeitende RNNs.
Bekannte Beispiele für Transformer-Modelle sind der Bidirectional Encoder Representations from Transformers (BERT) und die Generativen vortrainierten Transformer (GPT). Ersteres ist ein reines Encoder-Modell (linker Teil des Ablaufdiagramms), Letzteres (manche GPT) eine reine Decoder-Architektur (rechter Teil des Ablaufdiagramms).
Seitdem die Technik (Transformer) bekannt wurde, haben viele andere ML/DL-Modelle auch auf Transformer gesetzt, z. B. AlphaFold. Siehe dazu auch die Large Language Models (LLMs).

## Transformer-Architektur

Ein Transformer besteht in seiner ursprünglich vorgestellten Form im Wesentlichen aus in Serie geschalteten Kodierern (Encoder) und in Serie geschalteten Dekodierern (Decoder). Die Eingabesequenz wird durch eine sogenannte Embedding-Schicht in eine Vektorrepräsentation überführt. Die Gewichte der Embedding-Schicht werden während des Trainings angepasst. Im Falle des Transformers kommt zusätzlich eine Positionskodierung zum Einsatz, wodurch die sequentielle Abfolge der Wörter berücksichtigt werden kann. Ein Wort erhält somit zu Beginn eines Satzes eine andere Repräsentation als am Ende.
Die Eingabesequenz wird in der Vektorrepräsentation einer Serie von Kodierern übergeben und in eine interne Repräsentation überführt. Diese interne Repräsentation bildet die Bedeutung der Eingabesequenz abstrakt ab und wird durch die Dekodierer in eine Ausgabesequenz übersetzt. Die Eingabesequenz wird hierbei in Batches verarbeitet, wobei die Länge der Kodierer-Dekodierer-Pipeline die maximale Länge der Eingabesequenz beschränkt. Je nach Größe des Netzwerks können beispielsweise einzelne Sätze oder auch ganze Absätze verarbeitet werden. Bei Eingabesequenzen, welche kürzer sind als die Kodierer-Dekodierer-Pipeline, wird Padding zum Auffüllen der Eingabesequenz genutzt. Ein Kodierer besteht aus einem Selbst-Aufmerksamkeit-Modul (englisch self-attention) und einem Feed-Forward-Netz (FFN), während der Dekodierer aus einem Selbst-Aufmerksamkeit-Modul, einem Kodierer-Dekodierer-Aufmerksamkeit-Modul und einem Feedforward-Modul besteht.
Transformer sind ein moderner Ansatz, um die Probleme des Rechenaufwands durch eine Art von Parallelisierung von Algorithmen mittels Kodierern, Dekodierern und Aufmerksamkeitsmodulen zu lösen. Aufmerksamkeits-Module steigern die Verarbeitungsgeschwindigkeit, mit der das Modell von einer Sequenz in eine andere übersetzen kann.
Alle Kodierer haben die gleiche Architektur. Dekodierer sind einander auch sehr ähnlich. Jeder Kodierer besteht aus zwei Schichten: Self-Attention und einem Feed-Forward Netz (FNN). Die Eingaben des Kodierers durchlaufen zunächst ein Self-Attention Layer. Der Dekodierer verfügt über beide Ebenen, aber zwischen ihnen befindet sich ein Attention Layer, das dem Dekodierer hilft, sich auf relevante Teile der Eingabemenge zu konzentrieren. Außerdem sind in der Architektur mehrere Residualverbindungen und Layer-Normalisierungen enthalten.
Der essentielle Baustein des Transformer-Modells, der Encoder-Block (Abbildung links), ist eine Funktion 
  
    
      
        f
        :
        
          
            R
          
          
            
              t
              
                m
                a
                x
              
            
            ×
            d
          
        
        →
        
          
            R
          
          
            
              t
              
                m
                a
                x
              
            
            ×
            d
          
        
      
    
    {\displaystyle f\colon \mathbb {R} ^{t_{max}\times d}\to \mathbb {R} ^{t_{max}\times d}}
  
 mit 
  
    
      
        
          f
          
            θ
          
        
        (
        X
        )
        =
        Z
      
    
    {\displaystyle f_{\theta }(X)=Z}
  
, die definiert ist durch

  
    
      
        
          
            
              
                A
              
              
                
                =
                
                  
                    
                      1
                      d
                    
                  
                
                X
                
                  W
                  
                    (
                    q
                    )
                  
                
                (
                X
                
                  W
                  
                    (
                    k
                    )
                  
                
                
                  )
                  
                    T
                  
                
              
            
            
              
                M
              
              
                
                =
                
                  S
                  o
                  f
                  t
                  M
                  a
                  x
                
                (
                A
                )
                X
                
                  W
                  
                    (
                    v
                    )
                  
                
              
            
            
              
                O
              
              
                
                =
                
                  L
                  a
                  y
                  e
                  r
                  N
                  o
                  r
                  
                    m
                    
                      1
                    
                  
                
                (
                M
                +
                X
                )
              
            
            
              
                F
              
              
                
                =
                
                  R
                  e
                  L
                  U
                
                (
                O
                
                  W
                  
                    (
                    
                      f
                      
                        1
                      
                    
                    )
                  
                
                +
                
                  b
                  
                    (
                    
                      f
                      
                        1
                      
                    
                    )
                  
                
                )
                
                  W
                  
                    (
                    
                      f
                      
                        2
                      
                    
                    )
                  
                
                +
                
                  b
                  
                    (
                    
                      f
                      
                        2
                      
                    
                    )
                  
                
              
            
            
              
                Z
              
              
                
                =
                
                  L
                  a
                  y
                  e
                  r
                  N
                  o
                  r
                  
                    m
                    
                      2
                    
                  
                
                (
                O
                +
                F
                )
              
            
          
        
      
    
    {\displaystyle {\begin{aligned}A&={\sqrt {\frac {1}{d}}}XW^{(q)}(XW^{(k)})^{T}\\M&=\mathrm {SoftMax} (A)XW^{(v)}\\O&=\mathrm {LayerNorm_{1}} (M+X)\\F&=\mathrm {ReLU} (OW^{(f_{1})}+b^{(f_{1})})W^{(f_{2})}+b^{(f_{2})}\\Z&=\mathrm {LayerNorm_{2}} (O+F)\\\end{aligned}}}
  

Dabei wird die Softmax-Funktion und ein Rectifier (ReLU) verwendet. Jede Encoderschicht enthält zwei Unterschichten: die Selbst-Aufmerksamkeit und das Feed-Forward-Netzwerk (FFN).

### Kodierer

Die erste Teilschicht implementiert einen Mechanismus mit Mehrfach-Kopf Selbst-Aufmerksamkeit (englisch multi-head self-attention (MHA)). Dieser Mechanismus implementiert Heads, die eine linear projizierte Version der Abfragen, Schlüssel und Werte empfangen und parallel jeweils die gleiche Anzahl Ausgaben erzeugen, die dann zum Generieren eines Endergebnisses verwendet werden. Die zweite Teilschicht ist ein vollständig verbundenes Feedforward Neural Network, das aus zwei linearen Transformationen mit dazwischenliegender Aktivierung der Rectified Linear Unit (ReLU) besteht. Alle sechs Schichten des Kodierers wenden die gleichen linearen Transformationen auf alle Wörter in der Eingabesequenz an, aber jede Schicht verwendet dazu unterschiedliche Parameter. Auf jede Teilschicht folgt eine Normalisierungsschicht, die die berechnete Summe zwischen der Eingabe in die Teilschicht und der von der Teilschicht generierten Ausgabe normalisiert.
Die Transformer-Architektur kann grundsätzlich keine Informationen über die relativen Positionen der Wörter in der Sequenz erfassen, weil sie keine Wiederholung nutzt. Diese Informationen müssen durch die Kodierung der Positionen in die Eingabeeinbettungen eingefügt werden. Die Vektoren für die Kodierung der Positionen haben die gleiche Dimension wie die Eingabeeinbettungen und werden mithilfe von Sinus und Kosinus unterschiedlicher Frequenz generiert. Anschließend werden sie zu den Eingabeeinbettungen summiert, um die Positionsinformationen einzufügen.

### Dekodierer

Während der Inferenz kann ein Dekodierer zur autoregressiven Erzeugung von Sequenzen verwendet werden: Der Dekodierer wird mit einer Startsequenz abgefragt und sagt dann das nächste wahrscheinlichste Token vorher, welches im nächsten Schritt Teil der Eingabe wird (und so weiter). Beim Training des Dekodierers wird dieser Prozess durch das sogenannte „Teacher Forcing“ und Maskierung im Dekodierer ersetzt, womit das Training stark beschleunigt wird.
Jede Schicht Dekodierer enthält drei Teilschichten: die kausal maskierte Selbstaufmerksamkeit (englisch causally masked self-attention), die Kreuzaufmerksamkeit (englisch cross attention) und das Feedforward-Netzwerk (FFN). Weitere Details sind die residual connections eines Residual Neural Network und die Schichtnormalisierung (Funktion: LayerNorm), die zwar konzeptionell unnötig, aber für numerische Stabilität und Konvergenz erforderlich sind. Ähnlich wie die Feedforward-Netzwerkmodule einzeln auf jeden Vektor angewendet werden, wird auch LayerNorm einzeln auf jeden Vektor angewendet. Es werden zwei gängige Konventionen verwendet: die Post-LN- und die Pre-LN-Konvention. In der Post-LN-Konvention ist die Ausgabe jeder Teilschicht

  
    
      
        
          L
          a
          y
          e
          r
          N
          o
          r
          m
        
        (
        x
        +
        
          S
          u
          b
          l
          a
          y
          e
          r
        
        (
        x
        )
        )
      
    
    {\displaystyle \mathrm {LayerNorm} (x+\mathrm {Sublayer} (x))}
  

wobei 
  
    
      
        
          S
          u
          b
          l
          a
          y
          e
          r
        
        (
        x
        )
      
    
    {\displaystyle \mathrm {Sublayer} (x)}
  
 die von der Teilschicht selbst implementierte Funktion ist.
In der Pre-LN-Konvention ist die Ausgabe jeder Unterschicht

  
    
      
        x
        +
        
          S
          u
          b
          l
          a
          y
          e
          r
        
        (
        
          L
          a
          y
          e
          r
          N
          o
          r
          m
        
        (
        x
        )
        )
      
    
    {\displaystyle x+\mathrm {Sublayer} (\mathrm {LayerNorm} (x))}
  

Der ursprüngliche Transformer von 2017 verwendete die Post-LN-Konvention. Es war schwierig zu trainieren und erforderte eine sorgfältige Abstimmung der Hyperparameter und ein „Aufwärmen“ der Lernrate, bei dem sie klein beginnt und allmählich zunimmt. Die im Jahr 2018 vorgeschlagene Pre-LN-Konvention erwies sich als einfacher zu trainieren, da kein „Aufwärmen“ erforderlich ist und die Konvergenz somit schneller erfolgt.

### Ablaufdiagramme

## Attention-Modul

Die Aufgabe des Aufmerksamkeits-Bausteins (englisch attention) besteht darin, die Korrelation eines Eingabesymbols (Token) zu den anderen Eingabesymbolen zu berechnen. Gegeben sei die Worteinbettung 
  
    
      
        
          
            
              
                x
                →
              
            
          
          
            i
          
        
      
    
    {\displaystyle {\vec {x}}_{i}}
  
 des i-ten Tokens einer Sequenz. Diese Einbettung ist ein als Vektor kodiertes Eingabesymbol. Aus jeder Einbettung werden unabhängig voneinander drei Vektoren berechnet, indem die Einbettung mit einer jeweils erlernten Matrix 
  
    
      
        Q
      
    
    {\displaystyle Q}
  
, 
  
    
      
        K
      
    
    {\displaystyle K}
  
 oder 
  
    
      
        V
      
    
    {\displaystyle V}
  
 multipliziert wird:

  
    
      
        
          
            
              
                q
                →
              
            
          
          
            i
          
        
        =
        
          
            
              
                x
                →
              
            
          
          
            i
          
        
        ⋅
        Q
      
    
    {\displaystyle {\vec {q}}_{i}={\vec {x}}_{i}\cdot Q}
  
, der Abfragevektor (engl. query)

  
    
      
        
          
            
              
                k
                →
              
            
          
          
            i
          
        
        =
        
          
            
              
                x
                →
              
            
          
          
            i
          
        
        ⋅
        K
      
    
    {\displaystyle {\vec {k}}_{i}={\vec {x}}_{i}\cdot K}
  
, der Schlüsselvektor (engl. key)

  
    
      
        
          
            
              
                v
                →
              
            
          
          
            i
          
        
        =
        
          
            
              
                x
                →
              
            
          
          
            i
          
        
        ⋅
        V
      
    
    {\displaystyle {\vec {v}}_{i}={\vec {x}}_{i}\cdot V}
  
, der Wertevektor (engl. value)
Hieraus wird das Aufmerksamkeitsgewicht (englisch attention score) zwischen Token i und Token j der Sequenz durch das Skalarprodukt 
  
    
      
        
          s
          
            i
            ,
            j
          
        
      
    
    {\displaystyle s_{i,j}}
  
 berechnet

  
    
      
        
          s
          
            i
            ,
            j
          
        
        =
        
          
            
              
                q
                →
              
            
          
          
            i
          
        
        ⋅
        
          
            
              
                k
                →
              
            
          
          
            j
          
        
      
    
    {\displaystyle s_{i,j}={\vec {q}}_{i}\cdot {\vec {k}}_{j}}
  

und schließlich durch die Quadratwurzel der Länge der Schlüsselvektoren 
  
    
      
        dim
        ⁡
        (
        k
        )
      
    
    {\displaystyle \dim(k)}
  
 geteilt, um stabilere Gradienten zu erhalten (da die Softmax-Funktion bei großen absoluten Funktionsargumenten stark abflacht und der Gradient somit sehr klein wird):

  
    
      
        
          
            
              s
              
                i
                ,
                j
              
            
            
              dim
              ⁡
              (
              k
              )
            
          
        
      
    
    {\displaystyle {\frac {s_{i,j}}{\sqrt {\dim(k)}}}}
  

Hierauf wird die Softmax-Funktion 
  
    
      
        σ
      
    
    {\displaystyle \sigma }
  
 entlang der letzten Dimension angewandt:

  
    
      
        
          
            
              
                s
                ~
              
            
          
          
            i
          
        
        =
        σ
        
          (
          
            
              
                s
                
                  i
                  ,
                  j
                
              
              
                dim
                ⁡
                (
                k
                )
              
            
          
          )
        
      
    
    {\displaystyle {\tilde {s}}_{i}=\sigma \left({\frac {s_{i,j}}{\sqrt {\dim(k)}}}\right)}
  

Dieser skalare Wert wird nun mit dem Wertevektor multipliziert, was dazu führt, dass der Wertevektor mit einem Aufmerksamkeitsfaktor 
  
    
      
        
          
            
              
                s
                ~
              
            
          
          
            i
          
        
      
    
    {\displaystyle {\tilde {s}}_{i}}
  
 vergrößert oder verkleinert wird:

  
    
      
        
          
            
              
                z
                →
              
            
          
          
            i
          
        
        =
        
          
            
              
                s
                ~
              
            
          
          
            i
          
        
        ⋅
        
          
            
              
                v
                →
              
            
          
          
            i
          
        
        =
        σ
        
          (
          
            
              
                s
                
                  i
                  ,
                  j
                
              
              
                dim
                ⁡
                (
                k
                )
              
            
          
          )
        
        ⋅
        
          
            
              
                v
                →
              
            
          
          
            i
          
        
        ,
      
    
    {\displaystyle {\vec {z}}_{i}={\tilde {s}}_{i}\cdot {\vec {v}}_{i}=\sigma \left({\frac {s_{i,j}}{\sqrt {\dim(k)}}}\right)\cdot {\vec {v}}_{i},}
  

wobei der Vektor 
  
    
      
        
          
            
              
                z
                →
              
            
          
          
            i
          
        
      
    
    {\displaystyle {\vec {z}}_{i}}
  
 die berechnete Ausgabe des Attention-Moduls für Token i darstellt.

### Unterschiede zwischen Attention im Encoder und Decoder

Der Unterschied zwischen dem Self-Attention-Modul (im Encoder) und dem Kodierer-Dekodierer-Attention-Modul (im Decoder mit Encoder) besteht darin, dass das Self-Attention-Modul ausschließlich die Werte des vorhergehenden Kodierers bzw. Dekodierers verwendet und die Vektoren 
  
    
      
        
          
            
              
                q
                →
              
            
          
          
            i
          
        
      
    
    {\displaystyle {\vec {q}}_{i}}
  
, 
  
    
      
        
          
            
              
                k
                →
              
            
          
          
            i
          
        
      
    
    {\displaystyle {\vec {k}}_{i}}
  
 und 
  
    
      
        
          
            
              
                v
                →
              
            
          
          
            i
          
        
      
    
    {\displaystyle {\vec {v}}_{i}}
  
 berechnet. Das Kodierer-Dekodierer-Attention-Modul hingegen berechnet nur den Abfragevektor 
  
    
      
        
          
            
              
                q
                →
              
            
          
          
            i
          
        
      
    
    {\displaystyle {\vec {q}}_{i}}
  
 aus dem vorgelagerten Attention-Modul, während die Vektoren 
  
    
      
        
          
            
              
                k
                →
              
            
          
          
            i
          
        
      
    
    {\displaystyle {\vec {k}}_{i}}
  
 und 
  
    
      
        
          
            
              
                v
                →
              
            
          
          
            i
          
        
      
    
    {\displaystyle {\vec {v}}_{i}}
  
 aus dem Kodierer (Encoder) bezogen werden.

### Masked Attention

Die Maskierung der Attention (welche insbesondere im Decoder beim Training notwendig ist, damit nur vergangene Tokens beachtet werden) ist durch folgende Modifikation gegeben:

  
    
      
        
          
            
              
                
                  MaskedAttention
                
                (
                Q
                ,
                K
                ,
                V
                )
                =
                
                  softmax
                
                
                  (
                  
                    M
                    +
                    
                      
                        
                          Q
                          
                            K
                            
                              
                                T
                              
                            
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                  )
                
                V
                ,
              
            
          
        
      
    
    {\displaystyle {\begin{aligned}{\text{MaskedAttention}}(Q,K,V)={\text{softmax}}\left(M+{\frac {QK^{\mathrm {T} }}{\sqrt {d_{k}}}}\right)V,\end{aligned}}}
  

wobei M die Maskierungsmatrix ist, welche bei unmaskierten Werten den Wert 0 und bei maskierten Werten den Wert 
  
    
      
        −
        ∞
      
    
    {\displaystyle -\infty }
  
 annimmt. Stark negative Werte in der Maskierungsmatrix resultieren durch die Softmax-Funktion in einer maskierten Attention von Null.
Die Maske wird häufig so gewählt, dass nur auf vorhergehende Werte Wert gelegt wird, d. h., dass eine kausale Maskierung erfolgt.

### Multi-Head-Attention

In der Praxis wird die sogenannte Multi-Head-Attention (MHA) eingesetzt. Jeder Head besteht hierbei aus einer eigenen Version der Matrizen 
  
    
      
        Q
      
    
    {\displaystyle Q}
  
, 
  
    
      
        K
      
    
    {\displaystyle K}
  
 und 
  
    
      
        V
      
    
    {\displaystyle V}
  
. Jedes Attention-Modul besitzt mehrere Heads. Wenn ein Head für eine bestimmte Eingabe 
  
    
      
        x
      
    
    {\displaystyle x}
  
 nicht relevant ist, wird ein niedriger Wert berechnet, während ein für eine Eingabe relevanter Head einen hohen Ausgabewert berechnet.

### Scaled Dot-Product Attention

Der Transformer implementiert ein Scaled Dot-Product Attention, das dem Verfahren des allgemeinen Aufmerksamkeitsmechanismus folgt. Scaled Dot-Product Attention berechnet zunächst ein Skalarprodukt für jede Abfrage 
  
    
      
        q
      
    
    {\displaystyle q}
  
 mit allen Schlüsseln 
  
    
      
        k
      
    
    {\displaystyle k}
  
. Anschließend dividiert es jedes Ergebnis durch den Skalierungsfaktor 
  
    
      
        
          
            
              1
              
                
                  d
                  
                    k
                  
                
              
            
          
        
      
    
    {\displaystyle {\tfrac {1}{\sqrt {d_{k}}}}}
  
 und wendet dann die Softmax-Funktion an. Dabei erhält es die Gewichte, mit denen die Werte skaliert werden. In der Praxis können die Berechnungen effizient auf die gesamte Menge von Abfragen gleichzeitig angewendet werden. Zu diesem Zweck werden die Matrizen 
  
    
      
        Q
      
    
    {\displaystyle Q}
  
, 
  
    
      
        K
      
    
    {\displaystyle K}
  
 und 
  
    
      
        V
      
    
    {\displaystyle V}
  
 als Eingaben für die Aufmerksamkeitsfunktion attention bereitgestellt. Diese kann so dargestellt werden:

  
    
      
        
          a
          t
          t
          e
          n
          t
          i
          o
          n
        
        (
        Q
        ,
        K
        ,
        V
        )
        =
        
          s
          o
          f
          t
          m
          a
          x
        
        
          (
          
            
              
                Q
                
                  K
                  
                    T
                  
                
              
              
                
                  d
                  
                    k
                  
                
              
            
          
          )
        
        ⋅
        V
      
    
    {\displaystyle \mathrm {attention} (Q,K,V)=\mathrm {softmax} \left({\frac {QK^{T}}{\sqrt {d_{k}}}}\right)\cdot V}
  

Dieser Skalierungsfaktor wurde eingeführt, um dem Effekt entgegenzuwirken, dass die Skalarprodukte bei großen Werten stark ansteigen, wobei die Anwendung der Softmax-Funktion dann extrem kleine Gradienten zurückgeben würde, was zum Problem verschwindender Gradienten führen würde. Der Skalierungsfaktor dient dazu, die durch das Skalarprodukt berechneten Ergebnisse nach unten zu ziehen und dieses Problem zu vermeiden.
Das Verfahren zur Berechnung von 
  
    
      
        
          a
          t
          t
          e
          n
          t
          i
          o
          n
        
        (
        Q
        ,
        K
        ,
        V
        )
      
    
    {\displaystyle \mathrm {attention} (Q,K,V)}
  
 ist wie folgt:

Die Ausrichtungswerte werden berechnet, indem die in der Matrix 
  
    
      
        Q
      
    
    {\displaystyle Q}
  
 gespeicherte Menge von Abfragen mit den Schlüsseln in der Matrix 
  
    
      
        K
      
    
    {\displaystyle K}
  
 multipliziert wird. Wenn 
  
    
      
        Q
      
    
    {\displaystyle Q}
  
 eine 
  
    
      
        m
        ×
        
          d
          
            k
          
        
      
    
    {\displaystyle m\times d_{k}}
  
-Matrix und 
  
    
      
        K
      
    
    {\displaystyle K}
  
 eine 
  
    
      
        n
        ×
        
          d
          
            k
          
        
      
    
    {\displaystyle n\times d_{k}}
  
-Matrix ist, dann ist die resultierende Matrix 
  
    
      
        Q
        
          K
          
            T
          
        
      
    
    {\displaystyle QK^{T}}
  
 eine 
  
    
      
        m
        ×
        n
      
    
    {\displaystyle m\times n}
  
-Matrix:

  
    
      
        Q
        
          K
          
            T
          
        
        =
        
          
            (
            
              
                
                  
                    e
                    
                      11
                    
                  
                
                
                  
                    e
                    
                      12
                    
                  
                
                
                  ⋯
                
                
                  
                    e
                    
                      1
                      n
                    
                  
                
              
              
                
                  
                    e
                    
                      21
                    
                  
                
                
                  
                    e
                    
                      22
                    
                  
                
                
                  ⋯
                
                
                  
                    e
                    
                      2
                      n
                    
                  
                
              
              
                
                  ⋮
                
                
                  ⋮
                
                
                
                  ⋮
                
              
              
                
                  
                    e
                    
                      m
                      1
                    
                  
                
                
                  
                    e
                    
                      m
                      2
                    
                  
                
                
                  ⋯
                
                
                  
                    e
                    
                      m
                      n
                    
                  
                
              
            
            )
          
        
      
    
    {\displaystyle QK^{T}={\begin{pmatrix}e_{11}&e_{12}&\cdots &e_{1n}\\e_{21}&e_{22}&\cdots &e_{2n}\\\vdots &\vdots &&\vdots \\e_{m1}&e_{m2}&\cdots &e_{mn}\\\end{pmatrix}}}
  

Jeder der Ausrichtungswert wird mit 
  
    
      
        
          
            
              1
              
                
                  d
                  
                    k
                  
                
              
            
          
        
      
    
    {\displaystyle {\tfrac {1}{\sqrt {d_{k}}}}}
  
 skaliert:

  
    
      
        
          
            
              Q
              
                K
                
                  T
                
              
            
            
              
                d
                
                  k
                
              
            
          
        
        =
        
          
            (
            
              
                
                  
                    
                      
                        
                          e
                          
                            11
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
                
                  
                    
                      
                        
                          e
                          
                            12
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
                
                  ⋯
                
                
                  
                    
                      
                        
                          e
                          
                            1
                            n
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
              
              
                
                  
                    
                      
                        
                          e
                          
                            21
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
                
                  
                    
                      
                        
                          e
                          
                            22
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
                
                  ⋯
                
                
                  
                    
                      
                        
                          e
                          
                            2
                            n
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
              
              
                
                  ⋮
                
                
                  ⋮
                
                
                
                  ⋮
                
              
              
                
                  
                    
                      
                        
                          e
                          
                            m
                            1
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
                
                  
                    
                      
                        
                          e
                          
                            m
                            2
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
                
                  ⋯
                
                
                  
                    
                      
                        
                          e
                          
                            m
                            n
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
              
            
            )
          
        
      
    
    {\displaystyle {\frac {QK^{T}}{\sqrt {d_{k}}}}={\begin{pmatrix}{\tfrac {e_{11}}{\sqrt {d_{k}}}}&{\tfrac {e_{12}}{\sqrt {d_{k}}}}&\cdots &{\tfrac {e_{1n}}{\sqrt {d_{k}}}}\\{\tfrac {e_{21}}{\sqrt {d_{k}}}}&{\tfrac {e_{22}}{\sqrt {d_{k}}}}&\cdots &{\tfrac {e_{2n}}{\sqrt {d_{k}}}}\\\vdots &\vdots &&\vdots \\{\tfrac {e_{m1}}{\sqrt {d_{k}}}}&{\tfrac {e_{m2}}{\sqrt {d_{k}}}}&\cdots &{\tfrac {e_{mn}}{\sqrt {d_{k}}}}\\\end{pmatrix}}}
  

Es wird die Softmax-Funktion angewendet, um eine Menge von Gewichten zu erhalten.
Die resultierenden Gewichte werden mithilfe der Matrixmultiplikation auf die Elemente der 
  
    
      
        n
        ×
        
          d
          
            v
          
        
      
    
    {\displaystyle n\times d_{v}}
  
-Matrix 
  
    
      
        V
      
    
    {\displaystyle V}
  
 angewendet:

  
    
      
        
          s
          o
          f
          t
          m
          a
          x
        
        
          (
          
            
              
                Q
                
                  K
                  
                    T
                  
                
              
              
                
                  d
                  
                    k
                  
                
              
            
          
          )
        
        ⋅
        V
        =
        
          
            (
            
              
                
                  
                    s
                    o
                    f
                    t
                    m
                    a
                    x
                  
                  (
                  
                    
                      
                        
                          e
                          
                            11
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
                
                  
                    
                      
                        
                          e
                          
                            12
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
                
                  ⋯
                
                
                  
                    
                      
                        
                          e
                          
                            1
                            n
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                  )
                
              
              
                
                  
                    s
                    o
                    f
                    t
                    m
                    a
                    x
                  
                  (
                  
                    
                      
                        
                          e
                          
                            21
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
                
                  
                    
                      
                        
                          e
                          
                            22
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
                
                  ⋯
                
                
                  
                    
                      
                        
                          e
                          
                            2
                            n
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                  )
                
              
              
                
                  ⋮
                
                
                  ⋮
                
                
                
                  ⋮
                
              
              
                
                  
                    s
                    o
                    f
                    t
                    m
                    a
                    x
                  
                  (
                  
                    
                      
                        
                          e
                          
                            m
                            1
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
                
                  
                    
                      
                        
                          e
                          
                            m
                            2
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                
                
                  ⋯
                
                
                  
                    
                      
                        
                          e
                          
                            m
                            n
                          
                        
                        
                          
                            d
                            
                              k
                            
                          
                        
                      
                    
                  
                  )
                
              
            
            )
          
        
        ⋅
        
          
            (
            
              
                
                  
                    v
                    
                      11
                    
                  
                
                
                  
                    v
                    
                      12
                    
                  
                
                
                  ⋯
                
                
                  
                    v
                    
                      1
                      
                        d
                        
                          v
                        
                      
                    
                  
                
              
              
                
                  
                    v
                    
                      21
                    
                  
                
                
                  
                    v
                    
                      22
                    
                  
                
                
                  ⋯
                
                
                  
                    v
                    
                      2
                      
                        d
                        
                          v
                        
                      
                    
                  
                
              
              
                
                  ⋮
                
                
                  ⋮
                
                
                
                  ⋮
                
              
              
                
                  
                    v
                    
                      n
                      1
                    
                  
                
                
                  
                    v
                    
                      n
                      2
                    
                  
                
                
                  ⋯
                
                
                  
                    v
                    
                      n
                      
                        d
                        
                          v
                        
                      
                    
                  
                
              
            
            )
          
        
      
    
    {\displaystyle \mathrm {softmax} \left({\frac {QK^{T}}{\sqrt {d_{k}}}}\right)\cdot V={\begin{pmatrix}\mathrm {softmax} ({\tfrac {e_{11}}{\sqrt {d_{k}}}}&{\tfrac {e_{12}}{\sqrt {d_{k}}}}&\cdots &{\tfrac {e_{1n}}{\sqrt {d_{k}}}})\\\mathrm {softmax} ({\tfrac {e_{21}}{\sqrt {d_{k}}}}&{\tfrac {e_{22}}{\sqrt {d_{k}}}}&\cdots &{\tfrac {e_{2n}}{\sqrt {d_{k}}}})\\\vdots &\vdots &&\vdots \\\mathrm {softmax} ({\tfrac {e_{m1}}{\sqrt {d_{k}}}}&{\tfrac {e_{m2}}{\sqrt {d_{k}}}}&\cdots &{\tfrac {e_{mn}}{\sqrt {d_{k}}}})\\\end{pmatrix}}\cdot {\begin{pmatrix}v_{11}&v_{12}&\cdots &v_{1d_{v}}\\v_{21}&v_{22}&\cdots &v_{2d_{v}}\\\vdots &\vdots &&\vdots \\v_{n1}&v_{n2}&\cdots &v_{nd_{v}}\\\end{pmatrix}}}

## Adding Position Embeddings

Ein gängiger Ansatz besteht darin, der Eingabe Positionseinbettungen hinzuzufügen, bevor sie dem tatsächlichen Transformer-Modell zugeführt wird: Wenn 
  
    
      
        U
        ∈
        
          
            R
          
          
            
              t
              
                m
                a
                x
              
            
            ×
            d
          
        
      
    
    {\displaystyle U\in \mathbb {R} ^{t_{max}\times d}}
  
 die Matrix der Einheitseinbettungen ist, wird eine Matrix 
  
    
      
        P
        ∈
        
          
            R
          
          
            
              t
              
                m
                a
                x
              
            
            ×
            d
          
        
      
    
    {\displaystyle P\in \mathbb {R} ^{t_{max}\times d}}
  
 hinzugefügt, die die Positionsinformationen darstellt, und ihre Summe wird dem Transformer-Modell zugeführt: 
  
    
      
        T
        (
        U
        +
        P
        )
      
    
    {\displaystyle T(U+P)}
  
 . Für die erste Transformer-Ebene hat das folgenden Effekt:

  
    
      
        
          
            
              
                
                  
                    
                      A
                      ~
                    
                  
                
              
              
                
                =
                
                  
                    
                      1
                      d
                    
                  
                
                (
                U
                +
                P
                )
                
                  W
                  
                    (
                    q
                    )
                  
                
                
                  
                    
                      W
                      
                        (
                        k
                        )
                      
                    
                  
                  
                    T
                  
                
                (
                U
                +
                P
                
                  )
                  
                    T
                  
                
              
            
            
              
                
                  
                    
                      M
                      ~
                    
                  
                
              
              
                
                =
                
                  S
                  o
                  f
                  t
                  M
                  a
                  x
                
                (
                
                  
                    
                      A
                      ~
                    
                  
                
                )
                (
                U
                +
                P
                )
                
                  W
                  
                    (
                    v
                    )
                  
                
              
            
            
              
                
                  
                    
                      O
                      ~
                    
                  
                
              
              
                
                =
                
                  L
                  a
                  y
                  e
                  r
                  N
                  o
                  r
                  
                    m
                    
                      1
                    
                  
                
                (
                
                  
                    
                      M
                      ~
                    
                  
                
                +
                U
                +
                P
                )
              
            
            
              
                
                  
                    
                      F
                      ~
                    
                  
                
              
              
                
                =
                
                  R
                  e
                  L
                  U
                
                (
                
                  
                    
                      O
                      ~
                    
                  
                
                
                  W
                  
                    (
                    
                      f
                      
                        1
                      
                    
                    )
                  
                
                +
                
                  b
                  
                    (
                    
                      f
                      
                        1
                      
                    
                    )
                  
                
                )
                
                  W
                  
                    (
                    
                      f
                      
                        2
                      
                    
                    )
                  
                
                +
                
                  b
                  
                    (
                    
                      f
                      
                        2
                      
                    
                    )
                  
                
              
            
            
              
                
                  
                    
                      Z
                      ~
                    
                  
                
              
              
                
                =
                
                  L
                  a
                  y
                  e
                  r
                  N
                  o
                  r
                  
                    m
                    
                      2
                    
                  
                
                (
                
                  
                    
                      O
                      ~
                    
                  
                
                +
                
                  
                    
                      F
                      ~
                    
                  
                
                )
              
            
          
        
      
    
    {\displaystyle {\begin{aligned}{\tilde {A}}&={\sqrt {\frac {1}{d}}}(U+P)W^{(q)}{W^{(k)}}^{T}(U+P)^{T}\\{\tilde {M}}&=\mathrm {SoftMax} ({\tilde {A}})(U+P)W^{(v)}\\{\tilde {O}}&=\mathrm {LayerNorm_{1}} ({\tilde {M}}+U+P)\\{\tilde {F}}&=\mathrm {ReLU} ({\tilde {O}}W^{(f_{1})}+b^{(f_{1})})W^{(f_{2})}+b^{(f_{2})}\\{\tilde {Z}}&=\mathrm {LayerNorm_{2}} ({\tilde {O}}+{\tilde {F}})\\\end{aligned}}}
  

Dabei wird die Softmax-Funktion und ein Rectifier (ReLU) verwendet.

## Positional Encoding

Die Transformer-Architektur ist eine Architektur, die aus gestapelten Encoder-Schichten und Decoder-Schichten besteht. Zum Erzeugen von Sequenzdarstellungen nutzt der Transformer Self-Attention. Eine Encoder-Schicht besteht aus einer Self-Attention-Teilschicht, gefolgt von einer Feedforward-Teilschicht. Auf ähnliche Weise besteht eine Decoder-Schicht aus einer Self-Attention-Teilschicht, gefolgt von einer Encoder-Decodierer-Attention-Teilschicht, auf die eine Feedforward-Teilschicht folgt. Der Aufmerksamkeitsmechanismus ignoriert die Sequenzreihenfolge, weshalb in der Transformer-Architektur Positionskodierungen verwendet werden.

### Absolute Positional Encoding

In der ursprünglichen Transformer-Architektur wird zu jedem eingebetteten Quell- und Zielwort ein absoluter Positionskodierungsvektor 
  
    
      
        P
        
          E
          
            j
          
        
      
    
    {\displaystyle PE_{j}}
  
 hinzugefügt, um dessen Position 
  
    
      
        j
      
    
    {\displaystyle j}
  
 anzugeben. Die Idee besteht darin, Sinuskurven unterschiedlicher Wellenlängen zum Kodieren unterschiedlicher Positionen zu verwenden. Für die Position 
  
    
      
        j
        ∈
        {
        1
        ,
        …
        ,
        J
        }
      
    
    {\displaystyle j\in \{1,\ldots ,J\}}
  
 in einer Sequenz der Länge 
  
    
      
        J
      
    
    {\displaystyle J}
  
 wird der absolute Positionskodierungsvektor 
  
    
      
        P
        
          E
          
            j
          
        
        ∈
        
          
            R
          
          
            
              d
              
                
                  m
                  o
                  d
                  e
                  l
                
              
            
          
        
      
    
    {\displaystyle PE_{j}\in \mathbb {R} ^{d_{\mathrm {model} }}}
  
 definiert durch

  
    
      
        
          
            
              
                P
                
                  E
                  
                    j
                    ,
                    2
                    β
                  
                
              
              
                
                =
                sin
                ⁡
                (
                j
                
                  /
                
                
                  10000
                  
                    2
                    β
                    
                      /
                    
                    
                      d
                      
                        
                          m
                          o
                          d
                          e
                          l
                        
                      
                    
                  
                
                )
              
            
            
              
                P
                
                  E
                  
                    j
                    ,
                    2
                    β
                    +
                    1
                  
                
              
              
                
                =
                cos
                ⁡
                (
                j
                
                  /
                
                
                  10000
                  
                    2
                    β
                    
                      /
                    
                    
                      d
                      
                        
                          m
                          o
                          d
                          e
                          l
                        
                      
                    
                  
                
                )
              
            
          
        
      
    
    {\displaystyle {\begin{aligned}PE_{j,2\beta }&=\sin(j/10000^{2\beta /d_{\mathrm {model} }})\\PE_{j,2\beta +1}&=\cos(j/10000^{2\beta /d_{\mathrm {model} }})\\\end{aligned}}}
  

wobei 
  
    
      
        β
        ∈
        {
        1
        ,
        …
        ,
        ⌊
        
          
            
              
                d
                
                  
                    m
                    o
                    d
                    e
                    l
                  
                
              
              2
            
          
        
        ⌋
        }
      
    
    {\displaystyle \beta \in \{1,\ldots ,\lfloor {\tfrac {d_{\mathrm {model} }}{2}}\rfloor \}}
  
. Vaswani et al. schlagen vor, dass sinusförmige Positionseinbettungen genauso gut funktionieren wie erlernte Positionskodierungen, und sie stellen die Hypothese auf, dass erstere auf längere Sequenzen verallgemeinert werden können.

### Rotary Positional Embedding

Rotary Positional Embedding (RoPE) basiert auf einer Liste zweidimensionaler Vektoren 
  
    
      
        [
        (
        
          x
          
            1
          
          
            (
            1
            )
          
        
        ,
        
          x
          
            1
          
          
            (
            2
            )
          
        
        )
        ,
        (
        
          x
          
            2
          
          
            (
            1
            )
          
        
        ,
        
          x
          
            2
          
          
            (
            2
            )
          
        
        )
        ,
        (
        
          x
          
            3
          
          
            (
            1
            )
          
        
        ,
        
          x
          
            3
          
          
            (
            2
            )
          
        
        )
        ,
        …
        ]
      
    
    {\displaystyle [(x_{1}^{(1)},x_{1}^{(2)}),(x_{2}^{(1)},x_{2}^{(2)}),(x_{3}^{(1)},x_{3}^{(2)}),\dots ]}
  
. Ist ein Winkel 
  
    
      
        θ
      
    
    {\displaystyle \theta }
  
 vorgegeben, dann wird die RoPE-Kodierung für den Vektor 
  
    
      
        (
        
          x
          
            m
          
          
            (
            1
            )
          
        
        ,
        
          x
          
            m
          
          
            (
            2
            )
          
        
        )
      
    
    {\displaystyle (x_{m}^{(1)},x_{m}^{(2)})}
  
berechnet wie folgt:

  
    
      
        
          R
          o
          P
          E
        
        (
        
          x
          
            m
          
          
            (
            1
            )
          
        
        ,
        
          x
          
            m
          
          
            (
            2
            )
          
        
        ,
        m
        )
        =
        
          
            (
            
              
                
                  cos
                  ⁡
                  (
                  m
                  ⋅
                  θ
                  )
                
                
                  −
                  sin
                  ⁡
                  (
                  m
                  ⋅
                  θ
                  )
                
              
              
                
                  sin
                  ⁡
                  (
                  m
                  ⋅
                  θ
                  )
                
                
                  cos
                  ⁡
                  (
                  m
                  ⋅
                  θ
                  )
                
              
            
            )
          
        
        ⋅
        
          
            (
            
              
                
                  
                    x
                    
                      m
                    
                    
                      (
                      1
                      )
                    
                  
                
              
              
                
                  
                    x
                    
                      m
                    
                    
                      (
                      2
                      )
                    
                  
                
              
            
            )
          
        
        =
        
          
            (
            
              
                
                  
                    x
                    
                      m
                    
                    
                      (
                      1
                      )
                    
                  
                  ⋅
                  cos
                  ⁡
                  (
                  m
                  ⋅
                  θ
                  )
                  −
                  
                    x
                    
                      m
                    
                    
                      (
                      2
                      )
                    
                  
                  ⋅
                  sin
                  ⁡
                  (
                  m
                  ⋅
                  θ
                  )
                
              
              
                
                  
                    x
                    
                      m
                    
                    
                      (
                      2
                      )
                    
                  
                  ⋅
                  cos
                  ⁡
                  (
                  m
                  ⋅
                  θ
                  )
                  +
                  
                    x
                    
                      m
                    
                    
                      (
                      1
                      )
                    
                  
                  ⋅
                  sin
                  ⁡
                  (
                  m
                  ⋅
                  θ
                  )
                
              
            
            )
          
        
      
    
    {\displaystyle \mathrm {RoPE} (x_{m}^{(1)},x_{m}^{(2)},m)={\begin{pmatrix}\cos(m\cdot \theta )&-\sin(m\cdot \theta )\\\sin(m\cdot \theta )&\cos(m\cdot \theta )\\\end{pmatrix}}\cdot {\begin{pmatrix}x_{m}^{(1)}\\x_{m}^{(2)}\\\end{pmatrix}}={\begin{pmatrix}x_{m}^{(1)}\cdot \cos(m\cdot \theta )-x_{m}^{(2)}\cdot \sin(m\cdot \theta )\\x_{m}^{(2)}\cdot \cos(m\cdot \theta )+x_{m}^{(1)}\cdot \sin(m\cdot \theta )\\\end{pmatrix}}}
  

Die RoPE-Kodierung ist also einfach eine Multiplikation mit einem Winkel 
  
    
      
        θ
      
    
    {\displaystyle \theta }
  
, wenn die zweidimensionalen Vektoren als komplexe Zahlen 
  
    
      
        
          z
          
            m
          
        
        :=
        
          x
          
            m
          
          
            (
            1
            )
          
        
        +
        i
        ⋅
        
          x
          
            m
          
          
            (
            2
            )
          
        
      
    
    {\displaystyle z_{m}:=x_{m}^{(1)}+i\cdot x_{m}^{(2)}}
  
 dargestellt werden:

  
    
      
        
          R
          o
          P
          E
        
        (
        
          z
          
            m
          
        
        ,
        m
        )
        =
        
          e
          
            i
            ⋅
            m
            ⋅
            θ
          
        
        ⋅
        
          z
          
            m
          
        
      
    
    {\displaystyle \mathrm {RoPE} (z_{m},m)=e^{i\cdot m\cdot \theta }\cdot z_{m}}
  

Für eine Liste 
  
    
      
        2
        ⋅
        n
      
    
    {\displaystyle 2\cdot n}
  
-dimensionaler Vektoren wird eine RoPE-Kodierung durch eine endliche Folge 
  
    
      
        
          θ
          
            (
            1
            )
          
        
        ,
        …
        ,
        
          θ
          
            (
            n
            )
          
        
      
    
    {\displaystyle \theta ^{(1)},\dots ,\theta ^{(n)}}
  
 von Winkeln definiert. Dann wird die RoPE-Kodierung auf jedes Koordinatenpaar 
  
    
      
        (
        
          x
          
            m
          
          
            (
            1
            )
          
        
        ,
        
          x
          
            m
          
          
            (
            2
            )
          
        
        )
      
    
    {\displaystyle (x_{m}^{(1)},x_{m}^{(2)})}
  
 angewendet. Der Vorteil von RoPE besteht darin, dass das Skalarprodukt zwischen zwei Vektoren nur von ihrer relativen Position abhängt, denn es gilt

  
    
      
        
          R
          o
          P
          E
        
        (
        x
        ,
        m
        
          )
          
            T
          
        
        ⋅
        
          R
          o
          P
          E
        
        (
        y
        ,
        n
        )
        =
        
          R
          o
          P
          E
        
        (
        x
        ,
        m
        +
        k
        
          )
          
            T
          
        
        ⋅
        
          R
          o
          P
          E
        
        (
        y
        ,
        n
        +
        k
        )
      
    
    {\displaystyle \mathrm {RoPE} (x,m)^{T}\cdot \mathrm {RoPE} (y,n)=\mathrm {RoPE} (x,m+k)^{T}\cdot \mathrm {RoPE} (y,n+k)}
  

für jede positive ganze Zahl 
  
    
      
        k
      
    
    {\displaystyle k}
  
.

## Multimodalität

Transformer können auch für Modalitäten verwendet werden, die nicht textbasiert sind, indem man einen Weg findet, die Modalität in Token zu zerlegen. Eine Studie aus dem Jahr 2022 ergab, dass Transformer, die nur auf natürliche Sprache vortrainiert wurden, nur auf 0,03 % der Parameter feinabgestimmt werden können und bei vielen logischen und visuellen Aufgaben mit Long Short-Term Memory (LSTM) konkurrieren können, was ein Hinweis auf Transferleistungen bei Deep Learning (DL) ist.
Sogenannte „Vision Transformer“ passen den Transformer an Maschinelles Sehen an, indem sie Eingabebilder in eine Reihe von Patches zerlegen, sie in Vektoren umwandeln und sie wie Token in einem Standard-Transformer behandeln. Conformer und später Whisper folgen demselben Muster für die Spracherkennung, indem sie das Sprachsignal zunächst in ein Spektrogramm umwandeln, das dann wie ein Bild behandelt wird, d. h. in eine Reihe von Patches zerlegt, in Vektoren umgewandelt und wie Token in einem Standard-Transformer behandelt wird. Perceiver sind eine Variante von Transformern, die für Multimodalität entwickelt wurden. Beispiele für Bildgeneratoren, die multimodale Transformer verwenden, sind zum Beispiel DALL-E und Stable Diffusion. Im Gegensatz zu späteren Modellen ist DALL-E kein Diffusionsmodell. Stattdessen verwendet es einen Nur-Decoder-Transformer, der autoregressiv einen Text generiert, gefolgt von der Token-Darstellung eines Bildes, das dann von einem Variational Autoencoder in ein Bild umgewandelt wird.
