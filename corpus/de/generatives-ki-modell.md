---
title: Generatives KI-Modell
url: https://de.wikipedia.org/wiki/Generatives_KI-Modell
updated: '2026-10-21T04:40:40Z'
language: de
revision: '271497554'
license: CC BY-SA 4.0
source: Wikipedia
---

Ein generatives KI-Modell (englisch GenAI) ist ein Modell der künstlichen Intelligenz, das auf Grundlage erlernter Trainingsdaten neue Inhalte erzeugt, etwa Texte, Bilder, Audio, Video oder Programmcode. Generative KI-Modelle erlernen Muster und Strukturen vorgängig eingegebener Trainingsdaten und generieren daraus neue Daten mit ähnlichen Eigenschaften. Im Unterschied zu diskriminativen Modellen, die vorhandene Daten einordnen oder voneinander abgrenzen, bilden generative Modelle die statistischen Muster und Strukturen ihrer Trainingsdaten nach und produzieren daraus Ausgaben, die in den Trainingsdaten so nicht vorkamen.
Bekannte Anwendungen generativer KI-Modelle sind Chatbots wie ChatGPT oder Claude, Bildgeneratoren wie DALL-E oder Midjourney sowie Videogeneratoren wie Sora. Seit den 2020er Jahren hat die Verbreitung solcher Systeme durch Fortschritte im Deep Learning und die Entwicklung großer Sprachmodelle (LLMs) auf Basis der Transformer-Architektur stark zugenommen.
In der statistischen Klassifikation von KI gibt es zwei Hauptansätze, die als der generative Ansatz und der diskriminative Ansatz bezeichnet werden. Beide Ansätze berechnen Klassifikatoren durch unterschiedliche Methoden und unterscheiden sich im Grad der statistischen Modellierung.

## Generative Modelle

Üblicherweise basieren generative Klassifikatoren auf einem generativen Modell (gemeinsame Verteilung) und diskriminative Klassifikatoren auf einem diskriminativen Modell (bedingte Verteilung oder keine Verteilung), ohne zwischen den letzteren beiden Klassen zu unterscheiden.
Ein generatives Modell ist ein statistisches Modell der gemeinsamen Wahrscheinlichkeitsverteilung (P=Probabilität) 
  
    
      
        P
        (
        X
        ,
        Y
        )
      
    
    {\displaystyle P(X,Y)}
  
 auf einer gegebenen beobachtbaren Variablen X und einer Zielvariablen Y. Ein generatives Modell kann verwendet werden, um zufällige Ergebnisse einer Beobachtung x zu generieren.
Eine alternative, symmetrische Definition für die beiden Hauptansätze lautet für generative Modelle: Ein generatives Modell ist ein Modell der bedingten Wahrscheinlichkeitsverteilung der beobachtbaren Variablen X, gegeben eine Zielvariable y, symbolisch 
  
    
      
        P
        (
        X
        ∣
        Y
        =
        y
        )
      
    
    {\displaystyle P(X\mid Y=y)}
  
.
Dabei bezeichnet X eine beobachtbare Eingangsvariable mit spezifischen Einzelwerten x und Y eine Ziel- (Ausgangs-)variable mit spezifischen Werten/Objekten y (sogenannten Labels), welche bereits einer Klasse zugeordnet sind.

Unabhängig von der genauen Definition ist die Terminologie brauchbar, da ein generatives Modell verwendet werden kann, um zufällige Instanzen (Ergebnisse) entweder einer Beobachtung und einer Zielvariablen 
  
    
      
        (
        x
        ,
        y
        )
      
    
    {\displaystyle (x,y)}
  
 oder einer Beobachtung x gegeben einem Zielwert y zu generieren.
Der Begriff generatives Modell wird auch verwendet, um Modelle zu beschreiben, die Instanzen von Ausgabevariablen in einer Weise generieren, die keine klare Beziehung zu Wahrscheinlichkeitsverteilungen über potenzielle Stichproben von Eingabevariablen haben. Erzeugende gegnerische Netze (GANs) sind Beispiele für diese Klasse generativer Modelle und werden hauptsächlich nach der Ähnlichkeit bestimmter Ausgaben zu potenziellen Eingaben beurteilt. Solche Modelle sind keine Klassifikatoren.
Bei der Anwendung auf die Klassifikation ist die beobachtbare Variable X häufig eine kontinuierliche Variable, die Zielvariable Y ist im Allgemeinen eine diskrete Variable, die aus einer endlichen Menge von Labels besteht. Die bedingte Wahrscheinlichkeitsverteilung 
  
    
      
        P
        (
        Y
        ∣
        X
        )
      
    
    {\displaystyle P(Y\mid X)}
  
 kann auch als eine nicht-deterministische Zielfunktion 
  
    
      
        f
        :
        X
        →
        Y
      
    
    {\displaystyle f\colon X\to Y}
  
 interpretiert werden, wobei X als Eingaben und Y als Ausgaben betrachtet werden.

### Beziehungen zwischen beiden Definitionen

Gegeben eine endliche Menge von Labels, sind die beiden Definitionen eines generativen Modells eng miteinander verwandt. Ein Modell der bedingten Verteilung 
  
    
      
        P
        (
        X
        ∣
        Y
        =
        y
        )
      
    
    {\displaystyle P(X\mid Y=y)}
  
 ist ein Modell der Verteilung jedes Labels, und ein Modell der gemeinsamen Verteilung ist gleichwertig mit einem Modell der Verteilung der Labelwerte 
  
    
      
        P
        (
        Y
        )
      
    
    {\displaystyle P(Y)}
  
 zusammen mit der Verteilung der Beobachtungen gegeben ein Label 
  
    
      
        P
        (
        X
        ∣
        Y
        )
      
    
    {\displaystyle P(X\mid Y)}
  
 symbolisch 
  
    
      
        P
        (
        X
        ,
        Y
        )
        =
        P
        (
        X
        ∣
        Y
        )
        P
        (
        Y
        )
        .
      
    
    {\displaystyle P(X,Y)=P(X\mid Y)P(Y).}
  
. Während ein Modell der gemeinsamen Wahrscheinlichkeitsverteilung informativer ist als ein Modell der Verteilung der Label (aber ohne ihre relativen Häufigkeiten), ist es ein relativ kleiner Schritt, daher werden diese nicht immer unterschieden.
Gegeben ein Modell der gemeinsamen Verteilung 
  
    
      
        P
        (
        X
        ,
        Y
        )
      
    
    {\displaystyle P(X,Y)}
  
, können die Verteilungen der einzelnen Variablen als die marginalen Verteilungen 
  
    
      
        P
        (
        X
        )
        =
        
          ∑
          
            y
          
        
        P
        (
        X
        ,
        Y
        =
        y
        )
      
    
    {\displaystyle P(X)=\sum _{y}P(X,Y=y)}
  
 und 
  
    
      
        P
        (
        Y
        )
        =
        
          ∫
          
            x
          
        
        P
        (
        Y
        ,
        X
        =
        x
        )
      
    
    {\displaystyle P(Y)=\int _{x}P(Y,X=x)}
  
 berechnet werden (wobei X als kontinuierlich betrachtet wird, daher über sie integriert wird, und Y als diskret, daher über sie summiert wird), und jede bedingte Verteilung kann aus der Definition der bedingten Wahrscheinlichkeit berechnet werden: 
  
    
      
        P
        (
        X
        ∣
        Y
        )
        =
        P
        (
        X
        ,
        Y
        )
        
          /
        
        P
        (
        Y
        )
      
    
    {\displaystyle P(X\mid Y)=P(X,Y)/P(Y)}
  
 und 
  
    
      
        P
        (
        Y
        ∣
        X
        )
        =
        P
        (
        X
        ,
        Y
        )
        
          /
        
        P
        (
        X
        )
      
    
    {\displaystyle P(Y\mid X)=P(X,Y)/P(X)}
  
.
Gegeben ein Modell einer bedingten Wahrscheinlichkeitsverteilung und geschätzte Wahrscheinlichkeitsverteilungen für die Variablen X und Y, bezeichnet 
  
    
      
        P
        (
        X
        )
      
    
    {\displaystyle P(X)}
  
 und 
  
    
      
        P
        (
        Y
        )
      
    
    {\displaystyle P(Y)}
  
, kann die entgegengesetzte bedingte Wahrscheinlichkeitsverteilung mit Hilfe der Bayesschen Regel geschätzt werden:

  
    
      
        P
        (
        X
        ∣
        Y
        )
        P
        (
        Y
        )
        =
        P
        (
        Y
        ∣
        X
        )
        P
        (
        X
        )
        .
      
    
    {\displaystyle P(X\mid Y)P(Y)=P(Y\mid X)P(X).}
  
.
Zum Beispiel, gegeben ein generatives Modell für 
  
    
      
        P
        (
        X
        ∣
        Y
        )
      
    
    {\displaystyle P(X\mid Y)}
  
, kann geschätzt werden:

  
    
      
        P
        (
        Y
        ∣
        X
        )
        =
        P
        (
        X
        ∣
        Y
        )
        P
        (
        Y
        )
        
          /
        
        P
        (
        X
        )
        ,
      
    
    {\displaystyle P(Y\mid X)=P(X\mid Y)P(Y)/P(X),}
  

und gegeben ein diskriminatives Modell für 
  
    
      
        P
        (
        Y
        ∣
        X
        )
      
    
    {\displaystyle P(Y\mid X)}
  
 kann geschätzt werden:

  
    
      
        P
        (
        X
        ∣
        Y
        )
        =
        P
        (
        Y
        ∣
        X
        )
        P
        (
        X
        )
        
          /
        
        P
        (
        Y
        )
        .
      
    
    {\displaystyle P(X\mid Y)=P(Y\mid X)P(X)/P(Y).}
  

Beachte, dass die Bayessche-Regel (Berechnung einer bedingten Wahrscheinlichkeitsverteilung in Bezug auf die andere) und die Definition der bedingten Wahrscheinlichkeitsverteilung (Berechnung der bedingten Wahrscheinlichkeitsverteilung in Bezug auf die gemeinsame Verteilung) ebenfalls häufig miteinander verwechselt werden.

### Unterschied zu diskriminativen Klassifikatoren

Ein generativer Algorithmus modelliert, wie die Daten generiert wurden, um ein Signal zu kategorisieren. Er stellt die Frage: basierend auf meinen Generationsannahmen, welche Kategorie ist am wahrscheinlichsten, dieses Signal zu generieren? Ein diskriminativer Algorithmus kümmert sich nicht darum, wie die Daten generiert wurden, er kategorisiert einfach ein gegebenes Signal. Diskriminative Algorithmen versuchen, 
  
    
      
        p
        (
        y
        
          |
        
        x
        )
      
    
    {\displaystyle p(y|x)}
  
 direkt aus den Daten zu lernen und dann die Daten zu klassifizieren. Andererseits versuchen generative Algorithmen, 
  
    
      
        p
        (
        x
        ,
        y
        )
      
    
    {\displaystyle p(x,y)}
  
 zu lernen, was später in 
  
    
      
        p
        (
        y
        
          |
        
        x
        )
      
    
    {\displaystyle p(y|x)}
  
 umgewandelt werden kann, um die Daten zu klassifizieren. Einer der Vorteile generativer Algorithmen ist, dass man 
  
    
      
        p
        (
        x
        ,
        y
        )
      
    
    {\displaystyle p(x,y)}
  
 verwenden kann, um neue Daten ähnlich den bestehenden Daten zu generieren. Andererseits wurde gezeigt, dass einige diskriminative Algorithmen eine bessere Leistung erbringen als einige generative Algorithmen in Klassifikationsaufgaben.
Obwohl diskriminative Modelle die Verteilung der beobachteten Variablen nicht modellieren müssen, können sie im Allgemeinen keine komplexen Beziehungen zwischen den beobachteten und Zielvariablen ausdrücken. Aber im Allgemeinen schneiden sie bei Klassifikations- und Regressionsaufgaben nicht unbedingt besser ab als generative Modelle. Die beiden Klassen werden als komplementär oder als unterschiedliche Ansichten desselben Verfahrens angesehen.

### Tiefe generative Modelle

Mit dem Aufkommen des Deep Learnings entstand eine neue Familie von Methoden, die als tiefe, mehrschichtige generative Modelle (englisch DGMs) bezeichnet werden. Diese werden durch die Kombination von generativen Modellen in tiefen künstlichen neuronalen Netzen gebildet. Eine Zunahme des Umfangs neuronaler Netze geht typischerweise mit einer Zunahme des Umfangs der Trainingsdaten einher, was beides für eine gute Leistung erforderlich ist.
Zu den populären DGMs gehören Variational Autoencoders (VAEs), generative gegnerische Netzwerke (GANs) und autoregressive Modelle. In letzter Zeit gibt es einen Trend, sehr große, tiefe generative Modelle zu entwickeln. Zum Beispiel sind GPT-3 und sein Vorgänger GPT-2 autoregressive neuronale Sprachmodelle, die Milliarden von Parametern enthalten, sowie KI-Systeme, die zur Bildgenerierung verwendet werden und Milliarden Parameter haben können. Die elektronische Jukebox ist ein sehr großes generatives Modell für musikalisches Audio, welches ebenfalls Milliarden von Parametern enthält.

### Arten generativer Modelle

Hidden-Markov-Modell
Bayes-Klassifikator (z. B. Naive Bayes, autoregressives Modell)
Latente Dirichlet-Zuweisung
Boltzmann-Maschine (z. B. Eingeschränkte Boltzmann-Maschine, Deep Belief Network)
Variational Autoencoder (VAE)
Generatives gegnerisches Netz (GAN)
Diffusionsmodell (insbesondere zur Bilderzeugung)

## Diskriminative Modelle

Bei diskriminativen KI-Modellen werden Daten auf Grundlage von Unterschieden sortiert.
Ein diskriminatives Modell ist ein Modell der bedingten Wahrscheinlichkeitsverteilung 
  
    
      
        P
        (
        Y
        ∣
        X
        =
        x
        )
      
    
    {\displaystyle P(Y\mid X=x)}
  
 der Zielvariablen Y, gegeben eine Beobachtung x. Es kann verwendet werden, um den Wert der Zielvariablen Y bei gegebener Beobachtung x zu diskriminieren.
Bei der Anwendung auf die Klassifikation möchte man von einer Beobachtung x zu einem Label y (oder einer Wahrscheinlichkeitsverteilung über Labels) gelangen. Man kann dies direkt berechnen, ohne eine Wahrscheinlichkeitsverteilung zu verwenden (verteilungsfreier Klassifikator); man kann die Wahrscheinlichkeit eines Labels gegeben eine Beobachtung 
  
    
      
        P
        (
        Y
        
          |
        
        X
        =
        x
        )
      
    
    {\displaystyle P(Y|X=x)}
  
 (diskriminatives Modell) schätzen und darauf basierend klassifizieren; oder man kann die gemeinsame Verteilung 
  
    
      
        P
        (
        X
        ,
        Y
        )
      
    
    {\displaystyle P(X,Y)}
  
 (generatives Modell) schätzen, daraus die bedingte Wahrscheinlichkeit 
  
    
      
        P
        (
        Y
        
          |
        
        X
        =
        x
        )
      
    
    {\displaystyle P(Y|X=x)}
  
 berechnen und darauf basierend klassifizieren. Diese Ansätze sind zunehmend indirekt, aber zunehmend probabilistisch, was ermöglicht, mehr Domänenwissen und Wahrscheinlichkeitstheorie anzuwenden. In der Praxis werden je nach spezifischem Problem unterschiedliche Ansätze verwendet, und Hybride können die Stärken mehrerer Ansätze kombinieren.
Der Unterschied zwischen diskriminieren (unterscheiden) und klassifizieren ist subtil und wird nicht konsistent unterschieden.
Arten diskriminativer Modelle:

Logistische Regression
Support Vector Machines
Entscheidungsbaumlernen
Random Forest
Maximum-Entropie-Markov-Modelle

## Kritikpunkte

In welchem Ausmaß es möglich sein wird, die negativen Begleiteffekte für Mensch und Umwelt auf ein für Kritiker annehmbares Maß zu reduzieren ist derzeit noch offen, da mögliche Auswirkungen auf Nutzende derzeit noch erforscht werden. Neben dem sehr hohen Energiebedarf, konnten erste Studien mittlerweile nachteilige Auswirkungen auf Denkprozesse, sowie kognitive Fähigkeiten nachweisen.
Angesichts der vielfältigen Studienergebnisse warnte die Deutsche Gesetzliche Unfallversicherung 2026 vor den Auswirkungen. Sie ist der Ansicht, dass die Auswirkungen sowie der Einfluss, die generative KI-Anwendungen auf das menschliches Lernen und Denken haben oder haben könnten weiterhin genau beobachtet werden sollten. Schon jetzt lassen sich Auswirkungen auf neurologische Prozesse, aber auch auf koginitve Fähigkeiten, einschließlich Aufmerksamkeit, Fähigkeit zum Problemlösen, sowie das kritische Denken, nachweisen.
Als Beitrag zu einem Umgang mit generativer KI, der sowohl kritisch als auch zukunftsorientiert ausgerichtet ist, hat die Universität Hamburg dagegen folgende Kritikpunkte benannt:

geringere Entfaltung der individuellen Denkleistung
Datensicherheit, obliegt je nach Anwendung den Betreibenden, wodurch Nutzer an Einfluss verlieren
Diskriminierung, die aufgrund von unausgewogenen Trainingsdaten entsteht
wenige Betreiberunternehmen bilden Monopole, wobei sie ihre eigenen Regeln aufstellen
Hoher Ressourcenverbrauch (insbesondere Strom)
Ein weiteres Problem besteht in der Zuverlässigkeit der Angaben, die von diesen KI-Anwendungen gemacht werden. Die generierten Daten können frei erfunden sein. So wurden bereits im November 2025 über 300 Fälle bekannt, wo ChatGPT fiktive
Gerichtsurteile halluzinierte. Dies führte bei Rechtsprozessen zu Problemen, wo sich Anwälte auf diese vermeintlichen Präzedenzfälle beriefen.
