---
title: Generative Adversarial Networks
url: https://de.wikipedia.org/wiki/Generative_Adversarial_Networks
updated: '2026-03-14T07:03:39Z'
language: de
revision: '265198423'
license: CC BY-SA 4.0
source: Wikipedia
---

Generative Adversarial Networks (GAN, zu deutsch etwa „erzeugende gegnerische Netzwerke“) sind ein Konzept aus dem Maschinellen Lernen und beschreiben ein Framework für das Training von Netzwerken im Kontext von generativem Lernen bzw. unüberwachtem Lernen. Hierbei werden zwei Netzwerke, der Generator und der Diskriminator gegeneinander trainiert, wobei der Generator versucht Daten zu generieren, die einem ursprünglichen Datensatz sehr ähnlich sind, und der Diskriminator versucht echte und falsche Daten zu unterscheiden. Nach dem Training kann der Generator genutzt werden, um Daten zu generieren, die den ursprünglichen Daten sehr ähnlich sind.
GANs wurden 2014 von der Arbeitsgruppe um Ian Goodfellow vorgestellt und waren ein sehr prominenter Ansatz im generativen Lernen mit vielen Varianten wie z. B. StyleGAN. In der aktuellen Forschung wird der GAN-Ansatz oft zusätzlich mit anderen Ansätzen genutzt. So nutzt z. B. Stable Diffusion eine diskriminative Verlustfunktion im Training der first stage.

## Eigenschaften

Generative Adversarial Networks bestehen aus zwei künstlichen neuronalen Netzwerken, die ein Nullsummenspiel durchführen. Eines davon erstellt Kandidaten (der Generator), das zweite neuronale Netzwerk bewertet die Kandidaten (der Diskriminator). Typischerweise bildet der Generator von einem Vektor aus latenten Variablen auf den gewünschten Ergebnisraum ab. Ziel des Generators ist es zu lernen, Ergebnisse nach einer bestimmten Verteilung zu erzeugen. Der Diskriminator wird hingegen darauf trainiert, die Ergebnisse des Generators von den Daten aus der echten, vorgegebenen Verteilung zu unterscheiden. Die Zielfunktion des Generators besteht dann darin, Ergebnisse zu erzeugen, die der Diskriminator nicht unterscheiden kann. Dadurch soll sich die erzeugte Verteilung nach und nach an die echte Verteilung angleichen.
Das Training der beiden Netzwerke erfolgt gleichzeitig. Wie im maschinellen Lernen üblich, wird für das Training ein ausreichend großer Datensatz benötigt, der aus echten Daten besteht. Dieser Datensatz wird nur vom Diskriminator gesehen. Während des Trainings erzeugt der Generator Vektoren im Zielbereich der Daten basierend auf zufällig gewählten latenten Variablen. Der Diskriminator erhält sowohl die generierten als auch die echten Daten und versucht zu raten aus welcher Gruppe die jeweiligen Daten kommen. In jedem Trainingsschritt werden dann die Gewichte des Diskriminators und des Generators durch Backpropagation verbessert, wobei die Verlustfunktion für den Diskriminator ist, wie richtig der Diskriminator die Daten einsortiert hat, und die Verlustfunktion des Generators ist, wie sehr die generierten Daten vom Diskriminator als echte Daten missverstanden wurden. Durch dieses Vorgehen verbessern sich der Diskriminator und der Generator konstant gegenseitig, was bei einer ausreichenden Trainingszeit zu generierten Verteilungen führt, die nicht von echten zu unterscheiden sind.

### Mathematische Definition

Das ursprüngliche GAN ist als das folgende Spiel definiert:

Jeder Wahrscheinlichkeitsraum 
  
    
      
        (
        Ω
        ,
        
          μ
          
            r
            e
            f
          
        
        )
      
    
    {\displaystyle (\Omega ,\mu _{ref})}
  
 definiert ein GAN-Spiel.
Es gibt 2 Spieler: Generator und Diskriminator.
Die Strategiemenge des Generators ist 
  
    
      
        
          
            P
          
        
        (
        Ω
        )
      
    
    {\displaystyle {\mathcal {P}}(\Omega )}
  
, die Menge aller Wahrscheinlichkeitsmaße 
  
    
      
        
          μ
          
            G
          
        
      
    
    {\displaystyle \mu _{G}}
  
 auf 
  
    
      
        (
        Ω
        )
      
    
    {\displaystyle (\Omega )}
  
.
Die Strategiemenge des Diskriminators ist die Menge der Markov-Kerne 
  
    
      
        
          μ
          
            D
          
        
        :
        Ω
        →
        
          
            P
          
        
        [
        0
        ,
        1
        ]
      
    
    {\displaystyle \mu _{D}:\Omega \to {\mathcal {P}}[0,1]}
  
, wobei 
  
    
      
        
          
            P
          
        
        [
        0
        ,
        1
        ]
      
    
    {\displaystyle {\mathcal {P}}[0,1]}
  
 die Menge der Wahrscheinlichkeitsmaße auf 
  
    
      
        [
        0
        ,
        1
        ]
      
    
    {\displaystyle [0,1]}
  
.
Das GAN-Spiel ist ein Nullsummenspiel, mit der Zielfunktion 
  
    
      
        L
        (
        
          μ
          
            G
          
        
        ,
        
          μ
          
            D
          
        
        )
        :=
        
          
            E
          
          
            x
            ∼
            
              μ
              
                r
                e
                f
              
            
            ,
            y
            ∼
            
              μ
              
                D
              
            
            (
            x
            )
          
        
        [
        ln
        ⁡
        y
        ]
        +
        
          
            E
          
          
            x
            ∼
            
              μ
              
                G
              
            
            ,
            y
            ∼
            
              μ
              
                D
              
            
            (
            x
            )
          
        
        [
        ln
        ⁡
        (
        1
        −
        y
        )
        ]
      
    
    {\displaystyle L(\mu _{G},\mu _{D}):=\mathbb {E} _{x\sim \mu _{ref},y\sim \mu _{D}(x)}[\ln y]+\mathbb {E} _{x\sim \mu _{G},y\sim \mu _{D}(x)}[\ln(1-y)]}
  

Der Generator zielt darauf ab, das Ziel zu minimieren, und der Diskriminator zielt darauf ab, das Ziel zu maximieren.
Intuitiv gesprochen, besteht die Aufgabe des Generators darin, sich 
  
    
      
        
          μ
          
            G
          
        
        ≈
        
          μ
          
            r
            e
            f
          
        
      
    
    {\displaystyle \mu _{G}\approx \mu _{ref}}
  
, d. h., seine eigene Ausgangsverteilung so weit wie möglich an die Referenzverteilung anzugleichen; die Aufgabe des Diskriminators besteht darin, einen Wert nahe 1 auszugeben, wenn die Eingabe aus der Referenzverteilung zu stammen scheint, und einen Wert nahe 0 auszugeben, wenn die Eingabe so aussieht, als stamme sie aus der Generatorverteilung.

### Probleme

Die Konvergenz von Generative Adversarial Networks ist im heutigen Stand häufig problematisch. Während des Trainings kann es zu einem Moduskollaps kommen, wodurch der Generator nur noch eine begrenzte Anzahl hinreichend unterschiedlicher Stichproben erzeugt.
Typischerweise sind GANs empfindlich gegenüber der Initialisierung der Gewichte sowie der Hyperparameter.

## Verwendung

GANs wurden unter anderem zur Erstellung photorealistischer Bilder zur Visualisierung verschiedener Gegenstände, zur Modellierung von Bewegungsmustern in Videos, zur Erstellung von 3D-Modellen von Objekten aus 2D-Bildern und zur Bildbearbeitung astronomischer Bilder verwendet. GANs werden auch zur natürlichen Gestaltung der Nutzerinteraktion mit Chatbots verwendet. Weiterhin werden GANs in der Teilchenphysik dazu verwendet, zeitaufwendige Detektorsimulationen zu beschleunigen.

Des Weiteren können über Tools wie Real-ESRGAN eigene Bilder und Fotos über GANs hochskaliert werden. Abhängig von der Ausgangsstruktur funktioniert die Skalierung besser oder schlechter. Systematische oder geometrische Strukturen können gut hochskaliert werden, diffuse Texturen oder organische Strukturen hingegen bereiten noch Probleme.
GANs kommen zusätzlich im Bereich von verschiedenen Angriffen auf neuronale Netze zum Einsatz. Hierzu zählen unter anderem die Generierung von sogenannten Unrestricted Adversarial Examples oder Model Inversion Attacks, welche versuchen aus einem trainierten Modell Informationen zu den Trainingsdaten bzw. den gelernten Klassen zu extrahieren.

## Geschichte

Die Verwendung kompetitiver neuronaler Netzwerke wurde erstmals 2013 von Wei Li, Melvin Gauci und Roderich Gross vorgeschlagen. Das Konzept der Generative Adversarial Networks wurde 2014 von Yoshua Bengio, Ian Goodfellow, Jean Pouget-Abadie, Mehdi Mirza, Bing Xu, David Warde-Farley, Sherjil Ozair und Aaron Courville entwickelt. In Anlehnung an den Turing-Test wird die Methode auch als „Turing-Lernen“ (englisch Turing learning) bezeichnet.

## Alternative Modelle

Variational Autoencoder, Energiebasierte Modelle oder Normalizing-Flow-basierte Modelle sind alternative generative Modelle.
