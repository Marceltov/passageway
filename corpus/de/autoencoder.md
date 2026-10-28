---
title: Autoencoder
url: https://de.wikipedia.org/wiki/Autoencoder
updated: '2025-06-23T15:40:34Z'
language: de
revision: '257303441'
license: CC BY-SA 4.0
source: Wikipedia
---

Ein Autoencoder ist ein künstliches neuronales Netz, das dazu genutzt wird, effiziente Codierungen zu lernen.
Das Ziel eines Autoencoders ist es, eine komprimierte Repräsentation (Encoding) für einen Satz Daten zu lernen und somit auch wesentliche Merkmale zu extrahieren.
Dadurch kann er zur Dimensionsreduktion genutzt werden.

Der Autoencoder benutzt drei oder mehr Schichten:

Eine Eingabeschicht. Bei der Gesichtserkennung könnten die Neuronen beispielsweise die Pixel einer Fotografie abbilden.
Einige signifikant kleinere Schichten, die das Encoding bilden.
Eine Ausgabeschicht, in der jedes Neuron die gleiche Bedeutung hat wie das entsprechende in der Eingabeschicht.
Wenn lineare Neuronen benutzt werden, ist er der Hauptkomponentenanalyse sehr ähnlich.

## Definition

Ein Autoencoder ist ein geordnetes Tupel 
  
    
      
        (
        
          
            X
          
        
        ,
        
          
            Z
          
        
        ,
        (
        
          E
          
            ϕ
          
        
        
          )
          
            ϕ
            ∈
            Φ
          
        
        ,
        (
        
          D
          
            θ
          
        
        
          )
          
            θ
            ∈
            Θ
          
        
        )
      
    
    {\displaystyle ({\mathcal {X}},{\mathcal {Z}},(E_{\phi })_{\phi \in \Phi },(D_{\theta })_{\theta \in \Theta })}
  
, wobei 
  
    
      
        
          
            X
          
        
      
    
    {\displaystyle {\mathcal {X}}}
  
 ein messbarer Raum, 
  
    
      
        
          
            Z
          
        
      
    
    {\displaystyle {\mathcal {Z}}}
  
 eine beliebige Menge und 
  
    
      
        
          E
          
            ϕ
          
        
        :
        
          
            X
          
        
        →
        
          
            Z
          
        
        ,
        
          D
          
            θ
          
        
        :
        
          
            Z
          
        
        →
        
          
            X
          
        
      
    
    {\displaystyle E_{\phi }:{\mathcal {X}}\to {\mathcal {Z}},D_{\theta }:{\mathcal {Z}}\to {\mathcal {X}}}
  
 durch die Indexmengen 
  
    
      
        Φ
        ,
        Θ
      
    
    {\displaystyle \Phi ,\Theta }
  
 parametrisierte Funktionen sind. Die 
  
    
      
        
          E
          
            ϕ
          
        
      
    
    {\displaystyle E_{\phi }}
  
 werden Encoder und die 
  
    
      
        
          D
          
            θ
          
        
      
    
    {\displaystyle D_{\theta }}
  
 Decoder genannt.
In Anwendungen wird oft 
  
    
      
        
          
            X
          
        
        =
        
          
            R
          
          
            m
          
        
        ,
        
          
            Z
          
        
        =
        
          
            R
          
          
            n
          
        
      
    
    {\displaystyle {\mathcal {X}}=\mathbb {R} ^{m},{\mathcal {Z}}=\mathbb {R} ^{n}}
  
 für 
  
    
      
        m
        ≥
        n
      
    
    {\displaystyle m\geq n}
  
 gewählt. Für die Encoder und Decoder werden oft Familien von mehrlagigen Perzeptronen gewählt.
Intuitiv gesehen projiziert der Encoder die anfänglichen Daten in einen Raum mit üblicherweise tieferer Dimension, und der Decoder hat als Aufgabe, die ursprünglichen Daten wieder zu rekonstruieren. Das Ziel ist es nun, Encoder und Decoder so zu wählen, dass der Unterschied zwischen den ursprünglichen Daten und den rekonstruierten Daten möglichst gering ist. Dies formalisiert sich wie folgt.
Die Aufgabe des Autoencoders ist es, für eine gegebene Funktion 
  
    
      
        d
        :
        
          
            X
          
        
        ×
        
          
            X
          
        
        →
        [
        0
        ,
        ∞
        ]
      
    
    {\displaystyle d:{\mathcal {X}}\times {\mathcal {X}}\to [0,\infty ]}
  
 (
  
    
      
        d
      
    
    {\displaystyle d}
  
 kann beispielsweise eine Metrik sein) und eine gegebene Wahrscheinlichkeitsverteilung 
  
    
      
        μ
      
    
    {\displaystyle \mu }
  
 auf 
  
    
      
        
          
            X
          
        
      
    
    {\displaystyle {\mathcal {X}}}
  
 den erwarteten Rekonstruktionsfehler

  
    
      
        L
        (
        ϕ
        ,
        θ
        )
        =
        
          E
        
        [
        d
        (
        X
        ,
        
          D
          
            θ
          
        
        (
        
          E
          
            ϕ
          
        
        (
        X
        )
        )
        )
        ]
      
    
    {\displaystyle L(\phi ,\theta )=\mathbb {E} [d(X,D_{\theta }(E_{\phi }(X)))]}
  

zu minimieren. Hierbei bezeichnet 
  
    
      
        X
      
    
    {\displaystyle X}
  
 eine 
  
    
      
        μ
      
    
    {\displaystyle \mu }
  
-verteilte, 
  
    
      
        
          
            X
          
        
      
    
    {\displaystyle {\mathcal {X}}}
  
-wertige Zufallsvariable.
In Anwendungen ist oftmals 
  
    
      
        μ
        =
        
          
            1
            N
          
        
        
          ∑
          
            k
            =
            1
          
          
            N
          
        
        
          δ
          
            
              x
              
                k
              
            
          
        
      
    
    {\displaystyle \mu ={\frac {1}{N}}\sum _{k=1}^{N}\delta _{x_{k}}}
  
, wobei 
  
    
      
        (
        
          x
          
            1
          
        
        ,
        …
        ,
        
          x
          
            N
          
        
        )
      
    
    {\displaystyle (x_{1},\dots ,x_{N})}
  
 ein Datensatz bestehend aus 
  
    
      
        N
      
    
    {\displaystyle N}
  
 Datenpunkten ist (hier bezeichnet 
  
    
      
        
          δ
          
            x
          
        
      
    
    {\displaystyle \delta _{x}}
  
 das Dirac-Maß im Punkte 
  
    
      
        x
      
    
    {\displaystyle x}
  
, bzw. die empirische Dichtefunktion 
  
    
      
        
          
            
              μ
              ^
            
          
        
        (
        x
        )
        =
        
          
            1
            N
          
        
        
          ∑
          
            i
            =
            1
          
          
            N
          
        
        δ
        (
        x
        −
        
          x
          
            i
          
        
        )
      
    
    {\displaystyle {\hat {\mu }}(x)={\frac {1}{N}}\sum _{i=1}^{N}\delta (x-x_{i})}
  
 mit der Delta-Distribution). Zudem wird für 
  
    
      
        
          
            X
          
        
        =
        
          
            R
          
          
            m
          
        
      
    
    {\displaystyle {\mathcal {X}}=\mathbb {R} ^{m}}
  
 oftmals der quadratische Abstand 
  
    
      
        d
        (
        (
        
          x
          
            1
          
        
        ,
        …
        ,
        
          x
          
            m
          
        
        )
        ,
        (
        
          y
          
            1
          
        
        ,
        …
        ,
        
          y
          
            m
          
        
        )
        )
        =
        
          ∑
          
            k
            =
            1
          
          
            m
          
        
        (
        
          x
          
            k
          
        
        −
        
          y
          
            k
          
        
        
          )
          
            2
          
        
      
    
    {\displaystyle d((x_{1},\dots ,x_{m}),(y_{1},\dots ,y_{m}))=\sum _{k=1}^{m}(x_{k}-y_{k})^{2}}
  
 gewählt.

## Training

Das Training des Auto-Encoders besteht in der Suche nach 
  
    
      
        ϕ
        ∈
        Φ
        ,
        θ
        ∈
        Θ
      
    
    {\displaystyle \phi \in \Phi ,\theta \in \Theta }
  
, für die 
  
    
      
        L
        (
        ϕ
        ,
        θ
        )
      
    
    {\displaystyle L(\phi ,\theta )}
  
 möglichst klein wird.
Ein Autoencoder wird häufig mit einer der vielen Backpropagation-Varianten (CG-Verfahren, Gradientenverfahren etc.) trainiert. Obwohl diese Methode oft sehr effektiv ist, gibt es fundamentale Probleme damit, neuronale Netzwerke mit verborgenen Schichten zu trainieren. Sind die Fehler einmal zu den ersten paar Schichten rückpropagiert, werden sie unbedeutend. Das bedeutet, dass das Netzwerk fast immer lernt, den Durchschnitt der Trainingsdaten zu lernen. Obwohl es fortgeschrittene Backpropagation-Methoden (wie die conjugate gradient method) gibt, die diesem Problem zum Teil abhelfen, läuft dieses Verfahren auf langsames Lernen und schlechte Ergebnisse hinaus. Zur Verbesserung verwendet man initiale Gewichtungen, die dem Ergebnis schon ungefähr entsprechen. Dies wird Pretraining genannt.
Bei einer Pretraining-Technik, die von Geoffrey Hinton dazu entwickelt wurde, vielschichtige Autoencoder zu trainieren, werden benachbarte Schichten als Restricted Boltzmann Machine behandelt, um eine gute Annäherung zu erreichen und dann Backpropagation als Fine-Tuning zu benutzen.

## Erweiterungen

Variational Autoencoder erlauben das Generieren von neuen Daten, da als interne Repräsentation eine Parametrisierung einer Verteilung gelernt wird. Diffusions Modelle können als eine Art hierarchische Variational Autoencoder aufgefasst werden.
