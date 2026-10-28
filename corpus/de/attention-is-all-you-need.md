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

  
    
      
        
          
            
              
                x
                →
                
                  Encoder
                
                →
              
              
                z
              
            
            
              
                ↓
              
              
            
            
              
                (
                
                  y
                  
                    <
                    t
                  
                
                ,
              
              
                z
                )
                →
                
                  Decoder
                
                →
                p
                (
                
                  y
                  
                    t
                  
                
                ∣
                
                  y
                  
                    <
                    t
                  
                
                ,
                x
                )
              
            
          
        
      
    
    {\displaystyle {\begin{aligned}x\to {\text{Encoder}}\to &z\\\downarrow &\\(y_{<t},&z)\to {\text{Decoder}}\to p(y_{t}\mid y_{<t},x)\end{aligned}}}

### Encoder-Decoder-Architektur

Die Encoder-Decoder-Architektur lässt sich so beschreiben:

Encoder-Komponente: Der Encoder wandelt eine Eingabesequenz 
  
    
      
        x
        =
        (
        
          x
          
            1
          
        
        ,
        …
        ,
        
          x
          
            n
          
        
        )
      
    
    {\displaystyle x=(x_{1},\dots ,x_{n})}
  
 aus Tokens in eine kontinuierliche Repräsentation 
  
    
      
        z
        =
        (
        
          z
          
            1
          
        
        ,
        …
        ,
        
          z
          
            n
          
        
        )
      
    
    {\displaystyle z=(z_{1},\dots ,z_{n})}
  
 um, wobei jedes 
  
    
      
        
          z
          
            i
          
        
      
    
    {\displaystyle z_{i}}
  
 ein Vektor ist.
Decoder-Komponente: Der Decoder erhält als Input die vom Encoder erzeugte Repräsentation 
  
    
      
        z
      
    
    {\displaystyle z}
  
 sowie die bisher erzeugten Ausgabesymbole 
  
    
      
        
          y
          
            <
            t
          
        
        :=
        (
        
          y
          
            0
          
        
        ,
        
          y
          
            1
          
        
        ,
        …
        ,
        
          y
          
            t
            −
            1
          
        
        )
      
    
    {\displaystyle y_{<t}:=(y_{0},y_{1},\dots ,y_{t-1})}
  
 bis zum Zeitpunkt 
  
    
      
        t
      
    
    {\displaystyle t}
  
. Im ersten Schritt 
  
    
      
        t
        =
        1
      
    
    {\displaystyle t=1}
  
 gilt 
  
    
      
        
          y
          
            <
            t
          
        
        :=
        (
        
          y
          
            0
          
        
        )
      
    
    {\displaystyle y_{<t}:=(y_{0})}
  
 wobei 
  
    
      
        
          y
          
            0
          
        
        :=
        
          START
        
      
    
    {\displaystyle y_{0}:={\text{START}}}
  
 ein Startsymbol ist. Der Decoder gibt als Ausgabe eine bedingte Wahrscheinlichkeitsverteilung 
  
    
      
        p
        (
        
          y
          
            t
          
        
        ∣
        
          y
          
            <
            t
          
        
        ,
        x
        )
      
    
    {\displaystyle p(y_{t}\mid y_{<t},x)}
  
 über das nächste Ausgabesymbol 
  
    
      
        
          y
          
            t
          
        
      
    
    {\displaystyle y_{t}}
  
 zurück.
Die Eingaben 
  
    
      
        x
      
    
    {\displaystyle x}
  
 und 
  
    
      
        
          y
          
            <
            t
          
        
      
    
    {\displaystyle y_{<t}}
  
 werden zu Beginn durch eine Einbettungs-Funktion 
  
    
      
        h
      
    
    {\displaystyle h}
  
 in einen hochdimensionalen Raum eingebettet. Der Transformer lässt sich dann kompakt wie folgt verstehen:

  
    
      
        
          Transformer
        
        (
        x
        ,
        
          y
          
            <
            t
          
        
        )
        =
        
          Decoder
        
        (
        
          Encoder
        
        (
        h
        (
        x
        )
        )
        ,
        h
        (
        
          y
          
            <
            t
          
        
        )
        )
        =
        p
        (
        
          y
          
            t
          
        
        ∣
        
          y
          
            <
            t
          
        
        ,
        x
        )
        .
      
    
    {\displaystyle {\text{Transformer}}(x,y_{<t})={\text{Decoder}}({\text{Encoder}}(h(x)),h(y_{<t}))=p(y_{t}\mid y_{<t},x).}

#### Schichten des Encoders und Decoders

Encoder und Decoder bestehen jeweils aus gestapelten Schichten mit identischer Struktur. Sowohl der Encoder als auch der Decoder bestehen aus 
  
    
      
        N
      
    
    {\displaystyle N}
  
 identischen Schichten (im Original 
  
    
      
        N
        =
        6
      
    
    {\displaystyle N=6}
  
):

  
    
      
        
          Encoder
        
        (
        x
        )
        =
        
          
            S
          
          
            E
          
          
            (
            N
            )
          
        
        ∘
        ⋯
        ∘
        
          
            S
          
          
            E
          
          
            (
            1
            )
          
        
        (
        h
        (
        x
        )
        )
        ,
        
        
          Decoder
        
        (
        
          y
          
            <
            t
          
        
        ,
        z
        )
        =
        
          
            S
          
          
            D
          
          
            (
            N
            )
          
        
        ∘
        ⋯
        ∘
        
          
            S
          
          
            D
          
          
            (
            1
            )
          
        
        (
        h
        (
        
          y
          
            <
            t
          
        
        )
        ,
        z
        )
      
    
    {\displaystyle {\text{Encoder}}(x)={\text{S}}_{E}^{(N)}\circ \cdots \circ {\text{S}}_{E}^{(1)}(h(x)),\qquad {\text{Decoder}}(y_{<t},z)={\text{S}}_{D}^{(N)}\circ \cdots \circ {\text{S}}_{D}^{(1)}(h(y_{<t}),z)}
  

Eine Encoder-Schicht besteht wiederum aus zwei aufeinanderfolgenden Teilschichten 
  
    
      
        
          SubLayer
        
      
    
    {\displaystyle {\text{SubLayer}}}
  
, eine Decoder-Schicht hingegen aus drei aufeinanderfolgenden Teilschichten.

#### Teilschichten des Encoders und Decoders

Die Teilschichten 
  
    
      
        
          SubLayer
        
        ∈
        {
        
          MHA
        
        ,
        
          FFN
        
        }
      
    
    {\displaystyle {\text{SubLayer}}\in \{{\text{MHA}},{\text{FFN}}\}}
  
 des Encoders sind

Multi-Head Self-Attention 
  
    
      
        
          MHA
        
      
    
    {\displaystyle {\text{MHA}}}
  

position-wise Feedforward neural network 
  
    
      
        
          FFN
        
      
    
    {\displaystyle {\text{FFN}}}
  
.
Die Teilschichten 
  
    
      
        
          SubLayer
        
        ∈
        {
        
          MaskedMHA
        
        ,
        
          EncDecAtt
        
        ,
        
          FFN
        
        }
      
    
    {\displaystyle {\text{SubLayer}}\in \{{\text{MaskedMHA}},{\text{EncDecAtt}},{\text{FFN}}\}}
  
 des Decoder sind

Masked Multi-Head Self-Attention 
  
    
      
        
          MaskedMHA
        
      
    
    {\displaystyle {\text{MaskedMHA}}}
  

Encoder-Decoder-Attention 
  
    
      
        
          EncDecAtt
        
      
    
    {\displaystyle {\text{EncDecAtt}}}
  

position-wise Feedforward Neural Network 
  
    
      
        
          FFN
        
        .
      
    
    {\displaystyle {\text{FFN}}.}
  

Jede Teilschicht ist zudem mit einer Residual-Verbindung und anschließender Normalisierung versehen, das heißt, man addiert den Eingang zur Ausgabe der Teilschicht und normalisiert das Ergebnis:

  
    
      
        
          LayerNorm
        
        (
        x
        +
        
          SubLayer
        
        (
        x
        )
        )
        .
      
    
    {\displaystyle {\text{LayerNorm}}(x+{\text{SubLayer}}(x)).}
  

Es ist zu beachten, dass zwei Schichten innerhalb des Encoders respektive des Decoders denselben Aufbau besitzen, die einzelnen Teilschichten jeweils aber eigene Parameter haben.

##### Layer-Normalisierung

Die Layer-Normalisierung ist im Kern die aus der Statistik bekannte Standardisierung. Sei 
  
    
      
        s
        =
        (
        
          s
          
            1
          
        
        ,
        …
        ,
        
          s
          
            t
          
        
        )
      
    
    {\displaystyle s=(s_{1},\dots ,s_{t})}
  
 der Eingabevektor in 
  
    
      
        
          LayerNorm
        
        (
        s
        )
      
    
    {\displaystyle {\text{LayerNorm}}(s)}
  
, dann werden die einzelnen Komponenten von 
  
    
      
        s
      
    
    {\displaystyle s}
  
 mithilfe des empirischen Mittelwerts und der empirischen Varianz standardisiert:

  
    
      
        
          
            
              
                s
                
                  i
                
              
              ^
            
          
        
        =
        
          
            
              
                s
                
                  i
                
              
              −
              μ
            
            σ
          
        
        ,
        
        μ
        =
        
          
            1
            t
          
        
        
          ∑
          
            i
            =
            1
          
          
            t
          
        
        
          s
          
            i
          
        
        ,
        
        σ
        =
        
          
            
              
                1
                t
              
            
            
              ∑
              
                i
                =
                1
              
              
                t
              
            
            (
            
              s
              
                i
              
            
            −
            μ
            
              )
              
                2
              
            
          
        
      
    
    {\displaystyle {\widehat {s_{i}}}={\frac {s_{i}-\mu }{\sigma }},\qquad \mu ={\frac {1}{t}}\sum _{i=1}^{t}s_{i},\qquad \sigma ={\sqrt {{\frac {1}{t}}\sum _{i=1}^{t}(s_{i}-\mu )^{2}}}}
  

Auf das Resultat wird dann eine affine Transformation 
  
    
      
        s
        ↦
        a
        s
        +
        b
      
    
    {\displaystyle s\mapsto as+b}
  
 angewendet:

  
    
      
        
          f
          
            i
          
        
        (
        
          
            
              
                s
                
                  i
                
              
              ^
            
          
        
        )
        =
        
          g
          
            i
          
        
        
          
            
              
                s
                
                  i
                
              
              ^
            
          
        
        +
        
          b
          
            i
          
        
        ,
      
    
    {\displaystyle f_{i}({\widehat {s_{i}}})=g_{i}{\widehat {s_{i}}}+b_{i},}
  

wobei der Skalierungsvektor 
  
    
      
        g
        =
        (
        
          g
          
            1
          
        
        ,
        …
        ,
        
          g
          
            t
          
        
        )
      
    
    {\displaystyle g=(g_{1},\dots ,g_{t})}
  
 und der Verschiebungsvektor 
  
    
      
        b
        =
        (
        
          b
          
            1
          
        
        ,
        …
        ,
        
          b
          
            t
          
        
        )
      
    
    {\displaystyle b=(b_{1},\dots ,b_{t})}
  
 im Training gelernt werden.
Es gilt dann

  
    
      
        
          LayerNorm
        
        (
        s
        )
        =
        (
        
          f
          
            1
          
        
        (
        
          
            
              
                s
                
                  1
                
              
              ^
            
          
        
        )
        ,
        
        …
        ,
        
        
          f
          
            t
          
        
        (
        
          
            
              
                s
                
                  t
                
              
              ^
            
          
        
        )
        )
        =
        (
        
          g
          
            1
          
        
        
          
            
              
                s
                
                  1
                
              
              ^
            
          
        
        +
        
          b
          
            1
          
        
        ,
        
        …
        ,
        
        
          g
          
            t
          
        
        
          
            
              
                s
                
                  t
                
              
              ^
            
          
        
        +
        
          b
          
            t
          
        
        )
        .
      
    
    {\displaystyle {\text{LayerNorm}}(s)=(f_{1}({\widehat {s_{1}}}),\,\dots ,\,f_{t}({\widehat {s_{t}}}))=(g_{1}{\widehat {s_{1}}}+b_{1},\,\dots ,\,g_{t}{\widehat {s_{t}}}+b_{t}).}

### Einbettung mit Positional Encoding

Bevor die Eingabesequenzen 
  
    
      
        x
        =
        (
        
          x
          
            1
          
        
        ,
        …
        ,
        
          x
          
            n
          
        
        )
      
    
    {\displaystyle x=(x_{1},\dots ,x_{n})}
  
 im Encoder und 
  
    
      
        
          y
          
            <
            t
          
        
      
    
    {\displaystyle y_{<t}}
  
 im Decoder in das Modell eingegeben werden, werden die Eingaben zunächst in einen hochdimensionalen Vektorraum eingebettet und mit Informationen zur Position ergänzt:

  
    
      
        
          x
          
            i
          
        
        ↦
        
          Embedding
        
        (
        
          x
          
            i
          
        
        )
        +
        
          PE
        
        (
        i
        )
      
    
    {\displaystyle x_{i}\mapsto {\text{Embedding}}(x_{i})+{\text{PE}}(i)}
  

Da der Transformer keine rekurrente oder konvolutionelle Struktur besitzt, wird die Positionsinformation durch ein Positional Encoding ergänzt, das jeder Position 
  
    
      
        i
      
    
    {\displaystyle i}
  
 einen Vektor

  
    
      
        
          PE
        
        (
        i
        )
        =
        (
        
          PE
        
        (
        i
        ,
        0
        )
        ,
        
        
          PE
        
        (
        i
        ,
        1
        )
        ,
        
        …
        ,
        
        
          PE
        
        (
        i
        ,
        
          d
          
            model
          
        
        −
        1
        )
        )
        ∈
        
          
            R
          
          
            
              d
              
                model
              
            
          
        
      
    
    {\displaystyle {\text{PE}}(i)=({\text{PE}}(i,0),\,{\text{PE}}(i,1),\,\dots ,\,{\text{PE}}(i,d_{\text{model}}-1))\in \mathbb {R} ^{d_{\text{model}}}}
  

zuordnet. Die 
  
    
      
        k
      
    
    {\displaystyle k}
  
-te Komponente des Positional-Encoding-Vektors ist definiert durch:

  
    
      
        
          PE
        
        (
        i
        ,
        2
        k
        )
        =
        sin
        ⁡
        
          (
          
            
              i
              
                10000
                
                  2
                  k
                  
                    /
                  
                  
                    d
                    
                      model
                    
                  
                
              
            
          
          )
        
        ,
        
        
          PE
        
        (
        i
        ,
        2
        k
        +
        1
        )
        =
        cos
        ⁡
        
          (
          
            
              i
              
                10000
                
                  2
                  k
                  
                    /
                  
                  
                    d
                    
                      model
                    
                  
                
              
            
          
          )
        
      
    
    {\displaystyle {\text{PE}}(i,2k)=\sin \left({\frac {i}{10000^{2k/d_{\text{model}}}}}\right),\qquad {\text{PE}}(i,2k+1)=\cos \left({\frac {i}{10000^{2k/d_{\text{model}}}}}\right)}
  

wobei 
  
    
      
        i
      
    
    {\displaystyle i}
  
 der Positionsindex in der Sequenz 
  
    
      
        x
      
    
    {\displaystyle x}
  
.
Die kombinierte Einbettung ist dann definiert als die Matrix 
  
    
      
        h
        (
        x
        )
        ∈
        
          
            R
          
          
            n
            ×
            
              d
              
                model
              
            
          
        
      
    
    {\displaystyle h(x)\in \mathbb {R} ^{n\times d_{\text{model}}}}
  
, definiert als 
  
    
      
        h
        (
        x
        )
        =
        [
        
          h
          
            1
          
        
        (
        x
        )
        ,
        …
        ,
        
          h
          
            n
          
        
        (
        x
        )
        
          ]
          
            T
          
        
      
    
    {\displaystyle h(x)=[h_{1}(x),\dots ,h_{n}(x)]^{T}}
  
 mit

  
    
      
        
          h
          
            i
          
        
        (
        x
        )
        :=
        Embedding
        ⁡
        (
        
          x
          
            i
          
        
        )
        +
        
          PE
        
        (
        i
        )
      
    
    {\displaystyle h_{i}(x):=\operatorname {Embedding} (x_{i})+{\text{PE}}(i)}
  
,
wobei 
  
    
      
        i
      
    
    {\displaystyle i}
  
 der Positionsindex in der Sequenz 
  
    
      
        x
      
    
    {\displaystyle x}
  
 ist.
Als Veranschaulichung sei die Eingabesequenz 
  
    
      
        x
        =
        (
        
          Der
        
        ,
        
          Hund
        
        ,
        
          bellt
        
        ,
        …
        )
      
    
    {\displaystyle x=({\text{Der}},{\text{Hund}},{\text{bellt}},\dots )}
  
. Für das zweite Token 
  
    
      
        
          x
          
            2
          
        
        =
        
          Hund
        
      
    
    {\displaystyle x_{2}={\text{Hund}}}
  
 könnte die Einbettung und das Positional-Encoding beispielsweise wie folgt aussehen:

  
    
      
        
          h
          
            2
          
        
        (
        x
        )
        =
        
          Embedding
        
        (
        
          x
          
            2
          
        
        )
        +
        
          PE
        
        (
        2
        )
        =
        (
        0.2
        ,
        
        −
        0.4
        ,
        
        0.7
        ,
        …
        )
        +
        (
        0.91
        ,
        
        −
        0.42
        ,
        
        0.02
        ,
        …
        )
        .
      
    
    {\displaystyle h_{2}(x)={\text{Embedding}}(x_{2})+{\text{PE}}(2)=(0.2,\,-0.4,\,0.7,\dots )+(0.91,\,-0.42,\,0.02,\dots ).}

### Encoder

Jede Encoder-Schicht besteht aus zwei Teilschichten:

Multi-Head Self-Attention 
  
    
      
        
          MHA
        
      
    
    {\displaystyle {\text{MHA}}}
  
: ein Attentionmechanismus, bei dem Query, Key und Value aus derselben Eingabesequenz stammen, sodass für jedes Token Information aller Token der Sequenz entsprechend ihrer Relevanz kombiniert werden.
position-wise Feedforward neural network 
  
    
      
        
          FFN
        
      
    
    {\displaystyle {\text{FFN}}}
  
: Ein Feedforward-Netzwerk, das für jedes Token der Sequenz separat und mit denselben Parametern eine nichtlineare Transformation seiner Repräsentation durchführt, ohne Informationen zwischen den Tokens auszutauschen
Mit Layer-Normalisierung hat man

  
    
      
        
          
            
              
                
                  
                    S
                  
                  
                    MHA
                  
                  
                    E
                  
                
                (
                x
                )
              
              
                
                :=
                
                  LayerNorm
                
                (
                x
                +
                
                  MHA
                
                (
                x
                )
                )
              
            
            
              
                
                  
                    S
                  
                  
                    FFN
                  
                  
                    E
                  
                
                (
                x
                )
              
              
                
                :=
                
                  LayerNorm
                
                (
                x
                +
                
                  FFN
                
                (
                x
                )
                )
              
            
          
        
      
    
    {\displaystyle {\begin{aligned}{\text{S}}_{\text{MHA}}^{E}(x)&:={\text{LayerNorm}}(x+{\text{MHA}}(x))\\{\text{S}}_{\text{FFN}}^{E}(x)&:={\text{LayerNorm}}(x+{\text{FFN}}(x))\end{aligned}}}
  

Die 
  
    
      
        i
      
    
    {\displaystyle i}
  
-te Encoder-Schicht ist dann definiert als

  
    
      
        
          
            S
          
          
            E
            ,
            (
            i
            )
          
        
        (
        x
        )
        :=
        
          
            S
          
          
            FFN
          
          
            E
            ,
            (
            i
            )
          
        
        
          (
          
            
              
                S
              
              
                MHA
              
              
                E
                ,
                (
                i
                )
              
            
            (
            x
            )
          
          )
        
      
    
    {\displaystyle {\text{S}}^{E,(i)}(x):={\text{S}}_{\text{FFN}}^{E,(i)}\left({\text{S}}_{\text{MHA}}^{E,(i)}(x)\right)}
  

Der Encoder ist die Verkettung dieser Schichten:

  
    
      
        
          Encoder
        
        (
        x
        )
        =
        
          
            S
          
          
            E
            ,
            (
            N
            )
          
        
        ∘
        ⋯
        ∘
        
          
            S
          
          
            E
            ,
            (
            1
            )
          
        
        (
        x
        )
      
    
    {\displaystyle {\text{Encoder}}(x)={\text{S}}^{E,(N)}\circ \cdots \circ {\text{S}}^{E,(1)}(x)}

### Decoder

Jede Decoder-Schicht besteht aus:

Masked Multi-Head Self-Attention 
  
    
      
        
          MaskedMHA
        
      
    
    {\displaystyle {\text{MaskedMHA}}}
  
: Eine Variante der Multi-Head Self-Attention, bei der eine Maskierung verhindert, dass eine Position auf zukünftige Positionen zugreifen kann, wodurch die autoregressive Struktur erhalten bleibt
Encoder-Decoder-Attention 
  
    
      
        
          EncDecAtt
        
      
    
    {\displaystyle {\text{EncDecAtt}}}
  
: Ein Attention-Mechanismus, bei dem die Keys und Values aus der Ausgabe des Encoders stammen und die Queries aus dem Decoder, sodass der Decoder auf die kodierte Eingabesequenz zugreifen kann.
Position-wise Feedforward Neural Network 
  
    
      
        
          FFN
        
      
    
    {\displaystyle {\text{FFN}}}
  
.
Analog zum Encoder werden auch diese Normalisiert

  
    
      
        
          
            
              
                
                  
                    S
                  
                  
                    MaskedMHA
                  
                  
                    D
                  
                
                (
                y
                )
              
              
                
                :=
                
                  LayerNorm
                
                (
                y
                +
                
                  MaskedMHA
                
                (
                y
                )
                )
              
            
            
              
                
                  
                    S
                  
                  
                    EncDecAtt
                  
                  
                    D
                  
                
                (
                y
                ,
                z
                )
              
              
                
                :=
                
                  LayerNorm
                
                (
                y
                +
                
                  EncDecAtt
                
                (
                y
                ,
                z
                )
                )
              
            
            
              
                
                  
                    S
                  
                  
                    FFN
                  
                  
                    D
                  
                
                (
                y
                )
              
              
                
                :=
                
                  LayerNorm
                
                (
                y
                +
                
                  FFN
                
                (
                y
                )
                )
              
            
          
        
      
    
    {\displaystyle {\begin{aligned}{\text{S}}_{\text{MaskedMHA}}^{D}(y)&:={\text{LayerNorm}}(y+{\text{MaskedMHA}}(y))\\{\text{S}}_{\text{EncDecAtt}}^{D}(y,z)&:={\text{LayerNorm}}(y+{\text{EncDecAtt}}(y,z))\\{\text{S}}_{\text{FFN}}^{D}(y)&:={\text{LayerNorm}}(y+{\text{FFN}}(y))\end{aligned}}}
  

Die 
  
    
      
        i
      
    
    {\displaystyle i}
  
-te Decoder-Schicht ist dann definiert als

  
    
      
        
          
            S
          
          
            D
            ,
            (
            i
            )
          
        
        (
        y
        ,
        z
        )
        :=
        
          
            S
          
          
            FFN
          
          
            D
            ,
            (
            i
            )
          
        
        
          (
          
            
              
                S
              
              
                EncDecAtt
              
              
                D
                ,
                (
                i
                )
              
            
            
              (
              
                
                  
                    S
                  
                  
                    MaskedMHA
                  
                  
                    D
                    ,
                    (
                    i
                    )
                  
                
                (
                y
                )
                ,
                z
              
              )
            
          
          )
        
      
    
    {\displaystyle {\text{S}}^{D,(i)}(y,z):={\text{S}}_{\text{FFN}}^{D,(i)}\left({\text{S}}_{\text{EncDecAtt}}^{D,(i)}\left({\text{S}}_{\text{MaskedMHA}}^{D,(i)}(y),z\right)\right)}
  

Der Decoder ist die Verkettung dieser Schichten:

  
    
      
        
          Decoder
        
        (
        
          y
          
            <
            t
          
        
        ,
        z
        )
        =
        
          
            S
          
          
            D
            ,
            (
            N
            )
          
        
        ∘
        ⋯
        ∘
        
          
            S
          
          
            D
            ,
            (
            1
            )
          
        
        (
        
          y
          
            <
            t
          
        
        ,
        z
        )
      
    
    {\displaystyle {\text{Decoder}}(y_{<t},z)={\text{S}}^{D,(N)}\circ \cdots \circ {\text{S}}^{D,(1)}(y_{<t},z)}

### Position-wise Feedforward-Netzwerk

Jede Schicht enthält ein Feedforward-Netzwerk, das unabhängig auf jede Position angewendet wird und daher als position-wise Feedforward Neural Network bezeichnet wird. Es besteht aus zwei linearen Transformationen und einem Rectifier dazwischen:

  
    
      
        
          FFN
        
        (
        x
        )
        =
        max
        (
        0
        ,
        x
        
          W
          
            1
          
        
        +
        
          b
          
            1
          
        
        )
        
          W
          
            2
          
        
        +
        
          b
          
            2
          
        
      
    
    {\displaystyle {\text{FFN}}(x)=\max(0,xW_{1}+b_{1})W_{2}+b_{2}}

### Attention-Mechanismen

Beim Attention-Mechanismus werden zuerst aus der eingebetteten Eingabesequenz 
  
    
      
        h
        (
        x
        )
        ∈
        
          
            R
          
          
            n
            ×
            
              d
              
                model
              
            
          
        
      
    
    {\displaystyle h(x)\in \mathbb {R} ^{n\times d_{\text{model}}}}
  
 mittels lernbaren Gewichtsmatrizen 
  
    
      
        
          W
          
            Q
          
        
        ,
        
          W
          
            K
          
        
        ,
        
          W
          
            V
          
        
      
    
    {\displaystyle W^{Q},W^{K},W^{V}}
  
 lineare Projektionen berechnet, daraus resultieren drei Matrizen, welche als 
  
    
      
        Q
      
    
    {\displaystyle Q}
  
 („Query“), 
  
    
      
        K
      
    
    {\displaystyle K}
  
 („Key“)  und 
  
    
      
        V
      
    
    {\displaystyle V}
  
 („Value“) bezeichnet werden:

  
    
      
        Q
        (
        x
        )
        =
        h
        (
        x
        )
        
          W
          
            Q
          
        
        ∈
        
          
            R
          
          
            n
            ×
            
              d
              
                k
              
            
          
        
        ,
        
        K
        (
        x
        )
        =
        h
        (
        x
        )
        
          W
          
            K
          
        
        ∈
        
          
            R
          
          
            n
            ×
            
              d
              
                k
              
            
          
        
        ,
        
        V
        (
        x
        )
        =
        h
        (
        x
        )
        
          W
          
            V
          
        
        ∈
        
          
            R
          
          
            n
            ×
            
              d
              
                v
              
            
          
        
      
    
    {\displaystyle Q(x)=h(x)W^{Q}\in \mathbb {R} ^{n\times d_{k}},\quad K(x)=h(x)W^{K}\in \mathbb {R} ^{n\times d_{k}},\quad V(x)=h(x)W^{V}\in \mathbb {R} ^{n\times d_{v}}}
  

Metaphorisch lassen sich diese wie folgt interpretieren:

  
    
      
        Q
      
    
    {\displaystyle Q}
  
 beschreibt „was wird gesucht?“,

  
    
      
        K
      
    
    {\displaystyle K}
  
 beschreibt „welche Merkmale werden mit der Suche verglichen?“,

  
    
      
        V
      
    
    {\displaystyle V}
  
 beschreibt „welche Information wird geliefert?“.
Die tatsächliche Bedeutungen der drei Vektoren wird jedoch erst durch die im Training gelernten Projektionen erzeugt.

Die Attention berechnet Ähnlichkeiten zwischen 
  
    
      
        Q
      
    
    {\displaystyle Q}
  
 und 
  
    
      
        K
      
    
    {\displaystyle K}
  
 via Skalarprodukt und bildet daraus Gewichte 
  
    
      
        α
      
    
    {\displaystyle \alpha }
  
, mit Hilfe deren die 
  
    
      
        V
      
    
    {\displaystyle V}
  
-Vektoren gewichtet werden.
Man schreibt für die verschiedenen Formen von Attention statt 
  
    
      
        
          Attention
        
        (
        x
        )
      
    
    {\displaystyle {\text{Attention}}(x)}
  
 häufig 
  
    
      
        
          Attention
        
        (
        Q
        ,
        K
        ,
        V
        )
      
    
    {\displaystyle {\text{Attention}}(Q,K,V)}
  
, dies ist wie folgt zu verstehen

  
    
      
        x
        ↦
        h
        (
        x
        )
        ↦
        (
        Q
        (
        x
        )
        ,
        
        K
        (
        x
        )
        ,
        
        V
        (
        x
        )
        )
        ↦
        
          Attention
        
        (
        Q
        ,
        K
        ,
        V
        )
      
    
    {\displaystyle x\mapsto h(x)\mapsto (Q(x),\,K(x),\,V(x))\mapsto {\text{Attention}}(Q,K,V)}

#### Self-Attention und Cross-Attention

Man spricht von Self-Attention, wenn 
  
    
      
        Q
      
    
    {\displaystyle Q}
  
, 
  
    
      
        K
      
    
    {\displaystyle K}
  
 und 
  
    
      
        V
      
    
    {\displaystyle V}
  
 durch dieselbe Eingabesequenz erzeugt wurden. Man spricht von Cross-Attention, wenn 
  
    
      
        Q
      
    
    {\displaystyle Q}
  
 aus einer Sequenz kommt und 
  
    
      
        K
      
    
    {\displaystyle K}
  
 und 
  
    
      
        V
      
    
    {\displaystyle V}
  
 aus einer anderen Sequenz.
Beim Cross-Attention können dann die Sequenzlängen (das heißt Anzahl Tokens) auch unterschiedlich sein 
  
    
      
        n
        ≠
        m
      
    
    {\displaystyle n\neq m}
  

  
    
      
        Q
        (
        x
        )
        ∈
        
          
            R
          
          
            n
            ×
            
              d
              
                k
              
            
          
        
        ,
        
        K
        (
        x
        )
        ∈
        
          
            R
          
          
            m
            ×
            
              d
              
                k
              
            
          
        
        ,
        
        V
        (
        x
        )
        ∈
        
          
            R
          
          
            m
            ×
            
              d
              
                v
              
            
          
        
        .
      
    
    {\displaystyle Q(x)\in \mathbb {R} ^{n\times d_{k}},\quad K(x)\in \mathbb {R} ^{m\times d_{k}},\quad V(x)\in \mathbb {R} ^{m\times d_{v}}.}

#### Attention-Funktion auf einen Query

Für jeden Token gibt es einen Query 
  
    
      
        q
        ∈
        
          
            R
          
          
            
              d
              
                k
              
            
          
        
      
    
    {\displaystyle q\in \mathbb {R} ^{d_{k}}}
  
. Eine Attention-Funktion bildet einen Query 
  
    
      
        q
      
    
    {\displaystyle q}
  
 und eine Menge von Key-Value-Paaren 
  
    
      
        {
        (
        
          k
          
            i
          
        
        ,
        
          v
          
            i
          
        
        )
        
          }
          
            i
            =
            1
          
          
            n
          
        
      
    
    {\displaystyle \{(k_{i},v_{i})\}_{i=1}^{n}}
  
 auf einen mit Softmax gewichteten Vektor ab:

  
    
      
        
          Attention
        
        (
        q
        ,
        {
        (
        
          k
          
            i
          
        
        ,
        
          v
          
            i
          
        
        )
        
          }
          
            i
            =
            1
          
          
            n
          
        
        )
        =
        
          ∑
          
            i
            =
            1
          
          
            n
          
        
        
          α
          
            i
          
        
        
          v
          
            i
          
        
        ,
        
        
          α
          
            i
          
        
        :=
        
          
            softmax
          
          
            i
          
        
        
          (
          
            
              
                q
                ⋅
                
                  k
                  
                    i
                  
                
              
              
                
                  d
                  
                    k
                  
                
              
            
          
          )
        
        =
        
          
            
              exp
              ⁡
              (
              q
              ⋅
              
                k
                
                  i
                
              
              
                /
              
              
                
                  
                    d
                    
                      k
                    
                  
                
              
              )
            
            
              
                ∑
                
                  j
                
              
              exp
              ⁡
              (
              q
              ⋅
              
                k
                
                  j
                
              
              
                /
              
              
                
                  
                    d
                    
                      k
                    
                  
                
              
              )
            
          
        
        ,
        
        q
        ⋅
        
          k
          
            i
          
        
        :=
        
          ∑
          
            l
            =
            1
          
          
            
              d
              
                k
              
            
          
        
        
          q
          
            l
          
        
        
          k
          
            i
            l
          
        
        ,
      
    
    {\displaystyle {\text{Attention}}(q,\{(k_{i},v_{i})\}_{i=1}^{n})=\sum _{i=1}^{n}\alpha _{i}v_{i},\qquad \alpha _{i}:={\text{softmax}}_{i}\left({\frac {q\cdot k_{i}}{\sqrt {d_{k}}}}\right)={\frac {\exp(q\cdot k_{i}/{\sqrt {d_{k}}})}{\sum \limits _{j}\exp(q\cdot k_{j}/{\sqrt {d_{k}}})}},\qquad q\cdot k_{i}:=\sum \limits _{l=1}^{d_{k}}q_{l}k_{il},}
  

das heißt die Skalarprodukte 
  
    
      
        q
        ⋅
        
          k
          
            i
          
        
      
    
    {\displaystyle q\cdot k_{i}}
  
 werden mit 
  
    
      
        
          
            
              d
              
                k
              
            
          
        
      
    
    {\displaystyle {\sqrt {d_{k}}}}
  
 normalisiert (wobei 
  
    
      
        q
        ,
        
          k
          
            i
          
        
        ∈
        
          
            R
          
          
            
              d
              
                k
              
            
          
        
      
    
    {\displaystyle q,k_{i}\in \mathbb {R} ^{d_{k}}}
  
), um die Gewichte 
  
    
      
        
          α
          
            i
          
        
      
    
    {\displaystyle \alpha _{i}}
  
 zu bilden.

  
    
      
        q
        ⋅
        
          k
          
            i
          
        
      
    
    {\displaystyle q\cdot k_{i}}
  
 misst, wie ähnlich der Query 
  
    
      
        q
      
    
    {\displaystyle q}
  
 und der Key 
  
    
      
        
          k
          
            i
          
        
      
    
    {\displaystyle k_{i}}
  
 sind.

  
    
      
        
          
            
              d
              
                k
              
            
          
        
      
    
    {\displaystyle {\sqrt {d_{k}}}}
  
 wird zur Skalierung verwendet, damit die Skalarprodukte bei höherer Dimension stabil bleiben,

  
    
      
        
          α
          
            i
          
        
      
    
    {\displaystyle \alpha _{i}}
  
 gewichtet 
  
    
      
        
          v
          
            i
          
        
      
    
    {\displaystyle v_{i}}
  
 höher, wenn 
  
    
      
        
          k
          
            i
          
        
      
    
    {\displaystyle k_{i}}
  
 sehr ähnlich zu 
  
    
      
        q
      
    
    {\displaystyle q}
  
 ist.
Das bedeutet 
  
    
      
        
          k
          
            i
          
        
      
    
    {\displaystyle k_{i}}
  
 bestimmt, wie relevant das zugehörige 
  
    
      
        
          v
          
            i
          
        
      
    
    {\displaystyle v_{i}}
  
 auf den Query 
  
    
      
        q
      
    
    {\displaystyle q}
  
 ist.

#### Attention-Funktion auf alle Queries (Self-Attention und Cross-Attention)

Die Attention angewendet auf alle Queries:

  
    
      
        
          Attention
        
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
          
            
              
                Q
                
                  K
                  
                    T
                  
                
              
              
                
                  d
                  
                    k
                  
                
              
            
          
          )
        
        V
        =
        A
        V
        =
        O
        ,
      
    
    {\displaystyle {\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{T}}{\sqrt {d_{k}}}}\right)V=AV=O,}
  

im Falle von Self-Attention sind die Matrizen 
  
    
      
        A
        =
        [
        
          a
          
            i
            j
          
        
        ]
        ∈
        
          
            R
          
          
            n
            ×
            n
          
        
      
    
    {\displaystyle A=[a_{ij}]\in \mathbb {R} ^{n\times n}}
  
 und 
  
    
      
        O
        =
        [
        
          o
          
            i
            l
          
        
        ]
        ∈
        
          
            R
          
          
            n
            ×
            
              d
              
                v
              
            
          
        
      
    
    {\displaystyle O=[o_{il}]\in \mathbb {R} ^{n\times d_{v}}}
  
 definiert als

  
    
      
        
          a
          
            i
            j
          
        
        =
        
          
            
              exp
              ⁡
              (
              
                q
                
                  i
                
              
              ⋅
              
                k
                
                  j
                
              
              
                /
              
              
                
                  
                    d
                    
                      k
                    
                  
                
              
              )
            
            
              
                ∑
                
                  m
                  =
                  1
                
                
                  n
                
              
              exp
              ⁡
              (
              
                q
                
                  i
                
              
              ⋅
              
                k
                
                  m
                
              
              
                /
              
              
                
                  
                    d
                    
                      k
                    
                  
                
              
              )
            
          
        
        ,
        
        
          o
          
            i
            l
          
        
        =
        
          ∑
          
            j
            =
            1
          
          
            n
          
        
        
          a
          
            i
            j
          
        
        
          v
          
            j
            l
          
        
        .
      
    
    {\displaystyle a_{ij}={\frac {\exp(q_{i}\cdot k_{j}/{\sqrt {d_{k}}})}{\sum \limits _{m=1}^{n}\exp(q_{i}\cdot k_{m}/{\sqrt {d_{k}}})}},\qquad o_{il}=\sum \limits _{j=1}^{n}a_{ij}v_{jl}.}
  

Im Falle von Cross-Attention gilt 
  
    
      
        A
        =
        [
        
          a
          
            i
            j
          
        
        ]
        ∈
        
          
            R
          
          
            n
            ×
            m
          
        
      
    
    {\displaystyle A=[a_{ij}]\in \mathbb {R} ^{n\times m}}
  
 und 
  
    
      
        O
        =
        [
        
          o
          
            i
            l
          
        
        ]
        ∈
        
          
            R
          
          
            n
            ×
            
              d
              
                v
              
            
          
        
      
    
    {\displaystyle O=[o_{il}]\in \mathbb {R} ^{n\times d_{v}}}
  
 definiert als

  
    
      
        
          a
          
            i
            j
          
        
        =
        
          
            
              exp
              ⁡
              (
              
                q
                
                  i
                
              
              ⋅
              
                k
                
                  j
                
              
              
                /
              
              
                
                  
                    d
                    
                      k
                    
                  
                
              
              )
            
            
              
                ∑
                
                  s
                  =
                  1
                
                
                  m
                
              
              exp
              ⁡
              (
              
                q
                
                  i
                
              
              ⋅
              
                k
                
                  s
                
              
              
                /
              
              
                
                  
                    d
                    
                      k
                    
                  
                
              
              )
            
          
        
        ,
        
        
          o
          
            i
            l
          
        
        =
        
          ∑
          
            j
            =
            1
          
          
            m
          
        
        
          a
          
            i
            j
          
        
        
          v
          
            j
            l
          
        
        .
      
    
    {\displaystyle a_{ij}={\frac {\exp(q_{i}\cdot k_{j}/{\sqrt {d_{k}}})}{\sum \limits _{s=1}^{m}\exp(q_{i}\cdot k_{s}/{\sqrt {d_{k}}})}},\qquad o_{il}=\sum \limits _{j=1}^{m}a_{ij}v_{jl}.}

#### Verschiedene Formen von Attention

Masked Self-Attention: Im Decoder wird die Attention so eingeschränkt, dass jedes Element der Position 
  
    
      
        i
      
    
    {\displaystyle i}
  
 der Sequenz 
  
    
      
        (
        
          y
          
            1
          
        
        ,
        
          y
          
            2
          
        
        ,
        …
        ,
        
          y
          
            t
          
        
        )
      
    
    {\displaystyle (y_{1},y_{2},\dots ,y_{t})}
  
 nur seine und die früheren Positionen 
  
    
      
        1
        ,
        …
        ,
        i
      
    
    {\displaystyle 1,\dots ,i}
  
 berücksichtigt:

  
    
      
        
          MaskedMHA
        
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
          
            
              
                
                  Q
                  
                    K
                    
                      T
                    
                  
                
                
                  
                    d
                    
                      k
                    
                  
                
              
            
            +
            M
          
          )
        
        V
      
    
    {\displaystyle {\text{MaskedMHA}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{T}}{\sqrt {d_{k}}}}+M\right)V}
  

wobei 
  
    
      
        M
      
    
    {\displaystyle M}
  
 die Maskierungs-Matrix ist mit 
  
    
      
        
          M
          
            i
            j
          
        
        =
        0
      
    
    {\displaystyle M_{ij}=0}
  
 für erlaubte und 
  
    
      
        
          M
          
            i
            j
          
        
        =
        −
        ∞
      
    
    {\displaystyle M_{ij}=-\infty }
  
 für verbotene Positionen.
Encoder-Decoder-Attention: Queries stammen aus dem Decoder, Keys und Values aus dem Encoder:

  
    
      
        
          EncDecAtt
        
        (
        Q
        ,
        K
        ,
        V
        )
        ,
        
        
          mit 
        
        Q
        
           aus Decoder, 
        
        
        K
        
           und 
        
        V
        
           aus Encoder
        
        .
      
    
    {\displaystyle {\text{EncDecAtt}}(Q,K,V),\quad {\text{mit }}Q{\text{ aus Decoder, }}\quad K{\text{ und }}V{\text{ aus Encoder}}.}
  

Multi-Head Attention: Berechnet mehrere Attention-Köpfe parallel. Die Eingaben 
  
    
      
        Q
        ,
        K
        ,
        V
      
    
    {\displaystyle Q,K,V}
  
 stammen je nach Block aus Self-Attention (alle aus derselben Sequenz) oder aus der Encoder-Decoder-Attention (Query aus dem Decoder, Keys und Values aus dem Encoder):

  
    
      
        
          MHA
        
        (
        Q
        ,
        K
        ,
        V
        )
        =
        
          Concat
        
        (
        
          
            head
          
          
            1
          
        
        ,
        …
        ,
        
          
            head
          
          
            h
          
        
        )
        
          W
          
            O
          
        
      
    
    {\displaystyle {\text{MHA}}(Q,K,V)={\text{Concat}}({\text{head}}_{1},\dots ,{\text{head}}_{h})W^{O}}
  

mit:

  
    
      
        
          
            head
          
          
            i
          
        
        =
        
          Attention
        
        (
        Q
        
          W
          
            i
          
          
            Q
          
        
        ,
        K
        
          W
          
            i
          
          
            K
          
        
        ,
        V
        
          W
          
            i
          
          
            V
          
        
        )
      
    
    {\displaystyle {\text{head}}_{i}={\text{Attention}}(QW_{i}^{Q},KW_{i}^{K},VW_{i}^{V})}
  
.
Die Konkatenation 
  
    
      
        
          Concat
        
      
    
    {\displaystyle {\text{Concat}}}
  
 ist einfach das Aneinanderfügen von Vektoren, das heißt für zwei Vektor 
  
    
      
        
          v
          
            1
          
        
        =
        
          
            [
            
              
                
                  1
                
              
              
                
                  2
                
              
            
            ]
          
        
      
    
    {\displaystyle v_{1}={\begin{bmatrix}1\\2\end{bmatrix}}}
  
 und 
  
    
      
        
          v
          
            2
          
        
        =
        
          
            [
            
              
                
                  3
                
              
              
                
                  4
                
              
            
            ]
          
        
      
    
    {\displaystyle v_{2}={\begin{bmatrix}3\\4\end{bmatrix}}}
  
 ist die Operation definiert als

  
    
      
        
          Concat
        
        (
        
          v
          
            1
          
        
        ,
        
          v
          
            2
          
        
        )
        =
        
          
            [
            
              
                
                  1
                
              
              
                
                  2
                
              
              
                
                  3
                
              
              
                
                  4
                
              
            
            ]
          
        
        .
      
    
    {\displaystyle {\text{Concat}}(v_{1},v_{2})={\begin{bmatrix}1\\2\\3\\4\end{bmatrix}}.}

### Ausgabe

Die Wahrscheinlichkeit der gesamten Ausgabesequenz ist

  
    
      
        p
        (
        y
        ∣
        x
        )
        =
        
          ∏
          
            t
            =
            1
          
          
            T
          
        
        p
        (
        
          y
          
            t
          
        
        ∣
        
          y
          
            <
            t
          
        
        ,
        x
        )
        .
      
    
    {\displaystyle p(y\mid x)=\prod \limits _{t=1}^{T}p(y_{t}\mid y_{<t},x).}
  

Die Ausgabe ist nicht mehr Teil der Transformer-Architektur oder der Publikation, doch anschließend wird das nächste Symbol durch

  
    
      
        
          y
          
            t
          
        
        =
        
          
            
              a
              r
              g
              
              m
              a
              x
            
            
              y
              ∈
              V
            
          
        
        
        p
        (
        y
        ∣
        
          y
          
            <
            t
          
        
        ,
        x
        )
      
    
    {\displaystyle y_{t}={\underset {y\in V}{\operatorname {arg\,max} }}\;p(y\mid y_{<t},x)}
  

bestimmt, wobei 
  
    
      
        V
      
    
    {\displaystyle V}
  
 die Menge aller möglichen Ausgabesymbole ist.
