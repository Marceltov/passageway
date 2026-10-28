---
title: Künstliches Neuron
url: https://de.wikipedia.org/wiki/K%C3%BCnstliches_Neuron
updated: '2026-10-26T10:56:18Z'
language: de
revision: '271640734'
license: CC BY-SA 4.0
source: Wikipedia
---

Ein künstliches Neuron bildet die Basis für das Modell der künstlichen neuronalen Netze, ein Modell aus der Neuroinformatik, das durch biologische neuronale Netze motiviert ist. Als konnektionistisches Modell bilden sie in einem Netzwerk aus künstlichen Neuronen ein künstliches neuronales Netz und können so beliebig komplexe Funktionen approximieren, Aufgaben erlernen und Probleme lösen, bei denen eine explizite Modellierung schwierig bis nicht durchzuführen ist. Beispiele sind die Gesichts- und Spracherkennung.
Als Modell aus dem biologischen Vorbild der Nervenzelle entstanden, kann es mehrere Eingaben verarbeiten und entsprechend über seine Aktivierung reagieren. Dazu werden die Eingaben gewichtet an eine Ausgabefunktion übergeben, welche die Neuronenaktivierung berechnet. Ihr Verhalten wird ihnen im Allgemeinen durch Einlernen unter Verwendung eines Lernverfahrens gegeben.

## Geschichte

Die Anfänge der künstlichen Neuronen gehen auf Warren McCulloch und Walter Pitts im Jahr 1943 zurück. Sie zeigten an einem vereinfachten Modell eines Neuronalen Netzes, der McCulloch-Pitts-Zelle, dass diese logische und arithmetische Funktionen berechnen kann.

Die Hebbsche Lernregel wurde im Jahr 1949 von Donald Hebb beschrieben. Aufbauend auf der medizinischen Forschung von Santiago Ramón y Cajal, der bereits 1911 die Existenz von Synapsen nachgewiesen hatte, werden nach dieser Regel wiederholt aktive Verbindungen zwischen Nervenzellen gestärkt. Die Verallgemeinerung dieser Regel wird auch in den heutigen Lernverfahren noch verwendet.
Eine wichtige Arbeit kam im Jahre 1958 mit dem Konvergenztheorem über das Perzeptron heraus. Dort zeigte Frank Rosenblatt, dass es mit dem angegebenen Lernverfahren alle Lösungen einlernen kann, die mit diesem Modell repräsentierbar sind.
Jedoch zeigten die Kritiker Marvin Minsky und Seymour Papert 1969, dass ein einstufiges Perzeptron eine XOR-Verknüpfung nicht repräsentieren kann, weil die XOR-Funktion nicht linear separierbar (linear trennbar) ist, erst spätere Modelle konnten diesen Missstand beheben. Die so gezeigte Grenze in der Modellierung führte zunächst zu einem abnehmenden Interesse an der Erforschung der künstlichen neuronalen Netze sowie zu einer Streichung von Forschungsgeldern.
Ein Interesse an künstlichen Neuronalen Netzen kam erst wieder auf, als John Hopfield die Hopfield-Netze 1985 bekannt machte und zeigte, dass sie in der Lage sind Optimierungsprobleme zu lösen, wie das Problem des Handlungsreisenden. Ebenfalls führte die Arbeit zum Backpropagation-Verfahren von David E. Rumelhart, Geoffrey E. Hinton und Ronald J. Williams ab 1986 zu einer Wiederbelebung der Erforschung dieser Netze.
Heute werden solche Netze in vielen Forschungsbereichen verwendet.

## Biologische Motivation

Motiviert sind künstliche Neuronen durch die Nervenzellen der Säugetiere, die auf die Aufnahme und Verarbeitung von Signalen spezialisiert sind. Über Synapsen werden Signale elektrisch oder chemisch an andere Nervenzellen oder Effektorzellen (etwa zur Muskelkontraktion) weitergeleitet.
Eine Nervenzelle besteht aus dem Zellkörper, Axon und den Dendriten. Dendriten sind kurze Zellfortsätze, die stark verzweigt für die Aufnahme von Signalen anderer Nervenzellen oder Sinneszellen sorgen. Das Axon funktioniert als Signalausgang der Zelle und kann eine Länge von bis zu 1 m erreichen. Der Übergang der Signale erfolgt an den Synapsen, welche erregend oder hemmend wirken können.
Die Dendriten der Nervenzelle leiten die eingehenden elektrischen Erregungen an den Zellkörper weiter. Erreicht die Erregung einen gewissen Grenzwert und übersteigt ihn, entlädt sich die Spannung und pflanzt sich über das Axon fort (Alles-oder-nichts-Gesetz).
Die Verschaltung dieser Nervenzellen bildet die Grundlage für die geistige Leistung des Gehirns. Das Zentralnervensystem des Menschen besteht nach Schätzungen aus 1010 bis 1012 Nervenzellen, die durchschnittlich 10.000 Verbindungen besitzen – das menschliche Gehirn kann also mehr als 1014 Verbindungen besitzen. Das Aktionspotential im Axon kann sich mit einer Geschwindigkeit von bis zu 100 m/s fortpflanzen.
Im Vergleich zu Logikgattern zeigt sich auch die Effizienz von Neuronen. Während Gatter im Nanosekunden-Bereich (10−9) schalten, unter einem Energieverbrauch von 10−6 Joule (Daten von 1991), reagieren Nervenzellen im Millisekunden-Bereich (10−3) und verbrauchen lediglich eine Energie von 10−16 Joule. Trotz der augenscheinlich geringeren Werte in der Verarbeitung durch Nervenzellen können rechnergestützte Systeme nicht an die Fähigkeiten biologischer Systeme heranreichen.
Die Leistung neuronaler Netze wird ebenfalls durch die 100-Schritt-Regel demonstriert: Die visuelle Erkennung beim Menschen findet in maximal 100 sequentiellen Verarbeitungsschritten statt – die meist sequentiell arbeitenden Rechner erbringen keine vergleichbare Leistung.
Die Vorteile und Eigenschaften von Nervenzellen motivieren das Modell der künstlichen Neuronen. Viele Modelle und Algorithmen zu künstlichen neuronalen Netzen entbehren dennoch einer direkt plausiblen, biologischen Motivierung. Dort findet sich diese nur im Grundgedanken der abstrakten Modellierung der Nervenzelle.

## Modellierung

Mit der Biologie als Vorbild wird nun durch eine passende Modellbildung eine für die Informationstechnik verwendbare Lösung gefunden. Durch eine grobe Verallgemeinerung wird das System vereinfacht – unter Erhaltung der wesentlichen Eigenschaften.
Die Synapsen der Nervenzelle werden hierbei durch die Addition gewichteter Eingaben abgebildet, die Aktivierung des Zellkerns durch eine Aktivierungsfunktion mit Schwellenwert.
Die Verwendung eines Addierers und Schwellenwerts findet sich so schon in der McCulloch-Pitts-Zelle von 1943.

### Bestandteile

Ein künstliches Neuron mit dem Index 
  
    
      
        j
      
    
    {\displaystyle j}
  
 und den n Eingängen, indiziert mit 
  
    
      
        i
      
    
    {\displaystyle i}
  
, kann durch vier Basiselemente beschrieben werden:

Gewichtung: Jeder Eingang bekommt ein Gewicht. Die Gewichte 
  
    
      
        
          w
          
            i
            j
          
        
      
    
    {\displaystyle w_{ij}}
  
 (Eingang 
  
    
      
        i
      
    
    {\displaystyle i}
  
 bei Neuron 
  
    
      
        j
      
    
    {\displaystyle j}
  
) bestimmen den Grad des Einflusses, den die Eingaben des Neurons in der Berechnung der späteren Aktivierung einnehmen. Abhängig von den Vorzeichen der Gewichte kann eine Eingabe hemmend (inhibitorisch) oder erregend (exzitatorisch) wirken. Ein Gewicht von 0 markiert eine nicht existente Verbindung zwischen zwei Knoten.
Übertragungsfunktion: Die Übertragungsfunktion 
  
    
      
        Σ
      
    
    {\displaystyle \Sigma }
  
 berechnet anhand der Gewichtung der Eingaben die Netzeingabe des Neurons.
Aktivierungsfunktion: Die Ausgabe des Neurons wird schließlich durch die Aktivierungsfunktion 
  
    
      
        φ
      
    
    {\displaystyle \varphi }
  
 bestimmt. Die Aktivierung wird beeinflusst durch die Netzeingabe aus der Übertragungsfunktion sowie einem Schwellenwert.
Schwellenwert: Das Addieren eines Schwellenwerts 
  
    
      
        
          θ
          
            j
          
        
      
    
    {\displaystyle \theta _{j}}
  
 zur Netzeingabe verschiebt die gewichteten Eingaben. Die Bezeichnung ergibt sich aus der Verwendung einer Schwellenwertfunktion als Aktivierungsfunktion, bei der das Neuron aktiviert wird, wenn der Schwellenwert überschritten ist. Die biologische Motivierung dabei ist das Schwellenpotential bei Nervenzellen. Mathematisch gesehen wird die Trennebene, die den Merkmalsraum auftrennt, durch einen Schwellenwert mit einer Translation verschoben.
Durch einen Verbindungsgraphen werden folgende Elemente festgelegt:

Eingaben: Eingaben 
  
    
      
        
          x
          
            i
          
        
      
    
    {\displaystyle x_{i}}
  
 können einerseits aus dem beobachteten Prozess resultieren, dessen Werte dem Neuron übergeben werden, oder wiederum aus den Ausgaben anderer Neuronen stammen. Sie werden auch so dargestellt: 
Aktivierung oder Ausgabe: Das Ergebnis der Aktivierungsfunktion wird analog zur Nervenzelle als Aktivierung 
  
    
      
        
          o
          
            j
          
        
      
    
    {\displaystyle o_{j}}
  
 (o für „output“) des künstlichen Neurons mit dem Index 
  
    
      
        j
      
    
    {\displaystyle j}
  
 bezeichnet.

### Mathematische Definition

Das künstliche Neuron als Modell wird in der Literatur meist auf dem folgenden Weg eingeführt:
Zuerst wird die Aktivierung 
  
    
      
        v
      
    
    {\displaystyle v}
  
 (in der Abbildung oben als „Netzeingabe“ oder „net“ bezeichnet) des künstlichen Neurons durch

  
    
      
        v
        =
        
          ∑
          
            i
            =
            1
          
          
            n
          
        
        
          x
          
            i
          
        
        
          w
          
            i
          
        
        +
        
          w
          
            0
          
        
      
    
    {\displaystyle v=\sum _{i=1}^{n}x_{i}w_{i}+w_{0}}
  

definiert. Da die Mathematik den Index (0..9) und die Anzahl (10) im Allgemeinen nicht unterscheidet, wird als mathematische Vereinfachung normalerweise eine synthetische Eingabe 
  
    
      
        
          x
          
            0
          
        
        =
        1
      
    
    {\displaystyle x_{0}=1}
  
 eingeführt und man schreibt

  
    
      
        v
        =
        
          ∑
          
            i
            =
            0
          
          
            n
          
        
        
          x
          
            i
          
        
        
          w
          
            i
          
        
      
    
    {\displaystyle v=\sum _{i=0}^{n}x_{i}w_{i}}
  

  
    
      
        o
        =
        φ
        (
        v
        )
      
    
    {\displaystyle o=\varphi (v)}
  

Dabei ist

  
    
      
        n
      
    
    {\displaystyle n}
  
 die Anzahl der Eingaben

  
    
      
        
          x
          
            i
          
        
      
    
    {\displaystyle x_{i}}
  
 die Eingabe mit dem Index 
  
    
      
        i
      
    
    {\displaystyle i}
  
, die sowohl diskret als auch stetig sein kann

  
    
      
        
          w
          
            i
          
        
      
    
    {\displaystyle w_{i}}
  
 die Gewichtung der Eingabe mit dem Index 
  
    
      
        i
      
    
    {\displaystyle i}
  

  
    
      
        φ
      
    
    {\displaystyle \varphi }
  
 die Aktivierungsfunktion und

  
    
      
        o
      
    
    {\displaystyle o}
  
 die Ausgabe (englisch output)

## Aktivierungsfunktionen

Als Aktivierungsfunktion 
  
    
      
        φ
      
    
    {\displaystyle \varphi }
  
 können verschiedene Funktionstypen verwendet werden, abhängig von der verwendeten Netztopologie. Eine solche Funktion kann nicht-linear, zum Beispiel sigmoid, stückweise linear oder eine Sprungfunktion sein. Im Allgemeinen sind Aktivierungsfunktionen monoton steigend. Die letzte Aktivierungsfunktion bei der Ausgabeschicht des Neuronalen Netzes hat eine gewisse Nähe zur inversen Kopplungsfunktion in verallgemeinerten linearen Modellen und dient ähnlichen Zwecken.
Lineare Aktivierungsfunktionen unterliegen einer starken Beschränkung, da eine Komposition linearer Funktionen durch arithmetische Umformungen durch eine einzige lineare Funktion dargestellt werden kann. Für mehrschichtige Verbindungsnetzwerke sind sie deswegen nicht geeignet und finden so nur in einfachen Modellen Anwendung.
Beispiele für grundlegende Aktivierungsfunktionen sind:

### Schwellenwertfunktion

Die Schwellenwertfunktion (engl. hard limit), wie sie im Folgenden definiert ist, nimmt nur die Werte 
  
    
      
        0
      
    
    {\displaystyle 0}
  
 oder 
  
    
      
        1
      
    
    {\displaystyle 1}
  
 an. Den Wert 1 für die Eingabe 
  
    
      
        v
        ≥
        0
      
    
    {\displaystyle v\geq 0}
  
, sonst 
  
    
      
        0
      
    
    {\displaystyle 0}
  
. Bei subtraktiver Verwendung eines Schwellenwerts 
  
    
      
        θ
      
    
    {\displaystyle \theta }
  
 wird die Funktion nur aktiviert, wenn die zusätzliche Eingabe den Schwellenwert übersteigt. Ein Neuron mit einer solchen Funktion wird auch McCulloch-Pitts-Zelle genannt. Sie spiegelt die Alles-oder-nichts-Eigenschaft des Modells wider.

  
    
      
        
          φ
          
            hlim
          
        
        (
        v
        )
        =
        
          
            {
            
              
                
                  1
                
                
                  
                    wenn 
                  
                  v
                  ≥
                  0
                
              
              
                
                  0
                
                
                  
                    wenn 
                  
                  v
                  <
                  0
                
              
            
            
          
        
      
    
    {\displaystyle \varphi ^{\text{hlim}}(v)={\begin{cases}1&{\text{wenn }}v\geq 0\\0&{\text{wenn }}v<0\end{cases}}}
  

Ein Neuron mit dieser Aktivierungsfunktion wird auch so dargestellt:

### Stückweise lineare Funktion

Die hier verwendete stückweise lineare Funktion (engl. piecewise linear) bildet ein begrenztes Intervall linear ab, die äußeren Intervalle werden auf einen konstanten Wert abgebildet:

  
    
      
        
          φ
          
            pwl
          
        
        (
        v
        )
        =
        
          
            {
            
              
                
                  1
                
                
                  
                    wenn 
                  
                  v
                  ≥
                  
                    
                      1
                      2
                    
                  
                
              
              
                
                  v
                  +
                  
                    
                      1
                      2
                    
                  
                
                
                  
                    wenn 
                  
                  −
                  
                    
                      1
                      2
                    
                  
                  <
                  v
                  <
                  
                    
                      1
                      2
                    
                  
                
              
              
                
                  0
                
                
                  
                    wenn 
                  
                  v
                  ≤
                  −
                  
                    
                      1
                      2
                    
                  
                
              
            
            
          
        
      
    
    {\displaystyle \varphi ^{\text{pwl}}(v)={\begin{cases}1&{\text{wenn }}v\geq {\frac {1}{2}}\\v+{\frac {1}{2}}&{\text{wenn }}-{\frac {1}{2}}<v<{\frac {1}{2}}\\0&{\text{wenn }}v\leq -{\frac {1}{2}}\end{cases}}}
  

Ein Neuron mit der stückweise linearen Funktion als Aktivierungsfunktion wird auch folgendermaßen dargestellt:

### Sigmoidfunktion

Sigmoide Funktionen als Aktivierungsfunktion sind sehr häufig verwendete Abbildungen. Sie besitzen, wie hier definiert, ein variables Steigungsmaß 
  
    
      
        a
      
    
    {\displaystyle a}
  
, das die Krümmung des Funktionsgraphen beeinflusst. Eine spezielle Eigenschaft ist ihre Differenzierbarkeit, die für einige Verfahren wie den Backpropagation-Algorithmus benötigt werden:

  
    
      
        
          φ
          
            a
          
          
            sig
          
        
        (
        v
        )
        =
        
          
            1
            
              1
              +
              exp
              ⁡
              (
              −
              a
              v
              )
            
          
        
      
    
    {\displaystyle \varphi _{a}^{\text{sig}}(v)={\frac {1}{1+\exp(-av)}}}
  

Die Werte der obigen Funktionen liegen im Intervall 
  
    
      
        [
        0
        ,
        1
        ]
      
    
    {\displaystyle [0,1]}
  
. Für das Intervall 
  
    
      
        [
        −
        1
        ,
        +
        1
        ]
      
    
    {\displaystyle [-1,+1]}
  
 lassen sich diese Funktionen entsprechend definieren.
Ein Neuron mit der Sigmoidfunktion wird auch so dargestellt:

### Rectifier (ReLU)

Rectifier als Aktivierungsfunktion wird besonders in Deep-Learning-Modellen erfolgreich eingesetzt. Sie ist als Positivteil ihres Arguments definiert.

  
    
      
        φ
        (
        v
        )
        =
        max
        (
        0
        ,
        v
        )
      
    
    {\displaystyle \varphi (v)=\max(0,v)}

### Softplus

Softplus ist eine differenzierbare Alternative zur ReLU-Aktivierungsfunktion. Sie ist gegeben durch

  
    
      
        φ
        (
        v
        )
        =
        ln
        ⁡
        (
        1
        +
        exp
        ⁡
        (
        v
        )
        )
      
    
    {\displaystyle \varphi (v)=\ln(1+\exp(v))}
  

Ihre Ableitung ist eine Sigmoidfunktion.

### Gaussian Error Linear Unit (GELU)

In großen Transformerarchitekturen wird häufig auf GELU als Aktivierungsfunktion zurückgegriffen. Diese ist definiert als

  
    
      
        φ
        (
        v
        )
        =
        v
        ⋅
        Φ
        (
        v
        )
        ,
      
    
    {\displaystyle \varphi (v)=v\cdot \Phi (v),}
  

wobei 
  
    
      
        Φ
      
    
    {\displaystyle \Phi }
  
 die Verteilungsfunktion der Standardnormalverteilung bezeichnet.

## Beispiele

### Darstellung boolescher Funktionen

Mit künstlichen Neuronen lassen sich boolesche Funktionen darstellen. So können die drei Funktionen Konjunktion (and), Disjunktion (or) und Negation (not) unter Verwendung einer Schwellenwertfunktion 
  
    
      
        
          φ
          
            hlim
          
        
      
    
    {\displaystyle \varphi ^{\text{hlim}}}
  
 wie folgt repräsentiert werden:

Für die Konjunktion zum Beispiel ist ersichtlich, dass nur für die booleschen Eingaben 
  
    
      
        
          x
          
            1
          
        
        =
        1
      
    
    {\displaystyle x_{1}=1}
  
 und 
  
    
      
        
          x
          
            2
          
        
        =
        1
      
    
    {\displaystyle x_{2}=1}
  
 die Aktivierung

  
    
      
        o
        =
        
          φ
          
            hlim
          
        
        (
        (
        
          w
          
            1
          
        
        ⋅
        
          x
          
            1
          
        
        +
        
          w
          
            2
          
        
        ⋅
        
          x
          
            2
          
        
        )
        −
        θ
        )
        =
        
          φ
          
            hlim
          
        
        (
        (
        1
        
          ,
        
        0
        ⋅
        1
        +
        1
        
          ,
        
        0
        ⋅
        1
        )
        −
        1
        
          ,
        
        5
        )
        =
        
          φ
          
            hlim
          
        
        (
        0
        
          ,
        
        5
        )
        =
        1
      
    
    {\displaystyle o=\varphi ^{\text{hlim}}((w_{1}\cdot x_{1}+w_{2}\cdot x_{2})-\theta )=\varphi ^{\text{hlim}}((1{,}0\cdot 1+1{,}0\cdot 1)-1{,}5)=\varphi ^{\text{hlim}}(0{,}5)=1}
  

ergibt, sonst 
  
    
      
        0
      
    
    {\displaystyle 0}
  
.

### Einlernen eines Neurons

Anders als im vorherigen Beispiel, bei dem die passenden Gewichtungen gewählt wurden, können Neuronen die zu repräsentierende Funktion erlernen. Die Gewichtungen und der Schwellenwert werden anfangs mit zufälligen Werten belegt und anschließend unter Verwendung eines „Versuch-und-Irrtum“-Lernalgorithmus angepasst.

Um die logische Konjunktion zu erlernen, kann die Perzeptron-Kriteriumsfunktion angewendet werden. Sie addiert die Werte fehlerhaft erkannter Eingaben auf die Gewichtung hinzu, um die Erkennung zu verbessern, bis möglichst alle Eingaben richtig klassifiziert werden. Die Aktivierungsfunktion ist hier analog zum vorherigen Beispiel die Schwellenwertfunktion 
  
    
      
        
          φ
          
            hlim
          
        
      
    
    {\displaystyle \varphi ^{\text{hlim}}}
  
.
Für das Lernverfahren wird die Lernrate, welche die Geschwindigkeit des Einlernens festlegt, mit 
  
    
      
        α
        =
        1
      
    
    {\displaystyle \alpha =1}
  
 gewählt. Somit entfällt eine explizite Erwähnung.
Statt den Schwellenwert als solchen anzugeben, wird ein on-Neuron (Bias), also ein konstanter Eingang 
  
    
      
        
          x
          
            0
          
        
        =
        1
      
    
    {\displaystyle x_{0}=1}
  
 hinzugefügt. Der Schwellenwert wird durch die Gewichtung 
  
    
      
        
          w
          
            0
          
        
        =
        −
        θ
      
    
    {\displaystyle w_{0}=-\theta }
  
 angegeben.
Um das Neuron auf die beiden möglichen Ausgaben 
  
    
      
        0
      
    
    {\displaystyle 0}
  
 und 
  
    
      
        1
      
    
    {\displaystyle 1}
  
 der Konjunktion zu trainieren, werden die Eingaben für die zugehörige Ausgabe 
  
    
      
        0
      
    
    {\displaystyle 0}
  
 mit 
  
    
      
        −
        1
      
    
    {\displaystyle -1}
  
 multipliziert. Die Ausgabe ist durch diesen Schritt nur dann 
  
    
      
        0
      
    
    {\displaystyle 0}
  
, wenn die betreffende Eingabe fehlerhaft klassifiziert wurde. Dieses Vorgehen vereinfacht die Betrachtung beim Einlernen und die spätere Gewichtungsanpassung. Danach sieht die Lerntabelle folgendermaßen aus:

Der Eingang 
  
    
      
        
          x
          
            0
          
        
      
    
    {\displaystyle x_{0}}
  
 hat bei den Eingängen den Wert 
  
    
      
        −
        1
      
    
    {\displaystyle -1}
  
, bei denen das Neuron am Ende 
  
    
      
        0
      
    
    {\displaystyle 0}
  
 ausgeben soll.
Für die Ausgangssituation werden die Gewichtungen zufällig gewählt:

Zum Testen der Gewichtungen werden diese in ein Neuron mit drei Eingängen und dem Schwellenwert 
  
    
      
        θ
        =
        0
      
    
    {\displaystyle \theta =0}
  
 eingesetzt. Für die gewählten Gewichte sieht die Ausgabe wie folgt aus:

Die erste und dritte Eingabe werden falsch berechnet und das Neuron gibt 
  
    
      
        0
      
    
    {\displaystyle 0}
  
 aus. Nun findet die Perzeptron-Kriteriumsfunktion ihre Anwendung:
Durch die Addition mit den falsch erkannten Eingaben werden die zugehörigen Gewichte durch

  
    
      
        
          w
          
            i
          
          
            
              n
              e
              u
            
          
        
        =
        
          w
          
            i
          
          
            
              a
              l
              t
            
          
        
        +
        
          ∑
          
            j
          
        
        α
        ⋅
        (
        
          t
          
            j
          
        
        −
        
          o
          
            j
          
        
        )
        ⋅
        
          x
          
            i
          
        
      
    
    {\displaystyle w_{i}^{\mathrm {neu} }=w_{i}^{\mathrm {alt} }+\sum _{j}\alpha \cdot (t_{j}-o_{j})\cdot x_{i}}
  
 korrigiert.
Dabei ist

  
    
      
        j
      
    
    {\displaystyle j}
  
 die Nummer der Eingabe,

  
    
      
        
          t
          
            j
          
        
      
    
    {\displaystyle t_{j}}
  
 die gewünschte Ausgabe,

  
    
      
        
          o
          
            j
          
        
      
    
    {\displaystyle o_{j}}
  
 die tatsächliche Ausgabe,

  
    
      
        
          x
          
            i
          
        
      
    
    {\displaystyle x_{i}}
  
 die Eingabe des Neurons und

  
    
      
        α
        >
        0
      
    
    {\displaystyle \alpha >0}
  
 der Lerngeschwindigkeits-Koeffizient.

Die Überprüfung nach der Gewichtungsänderung zeigt, dass statt der ersten und dritten Eingabe nun die vierte Eingabe falsch klassifiziert wird. Die Ausführung eines weiteren Schrittes des Lernverfahrens verbessert die Erkennungsfunktion des Neurons:

Nun sieht man, dass das Neuron die vorgegebene Funktion erlernt hat und alle vier Eingaben richtig berechnet.
Unter Verwendung der Eingabe 
  
    
      
        
          x
          
            1
          
        
        =
        1
      
    
    {\displaystyle x_{1}=1}
  
 und 
  
    
      
        
          x
          
            2
          
        
        =
        1
      
    
    {\displaystyle x_{2}=1}
  
 und die Wahl von 
  
    
      
        θ
        =
        −
        
          w
          
            0
          
        
      
    
    {\displaystyle \theta =-w_{0}}
  
 folgt nun die Aktivierung:

  
    
      
        
          
            
              
                o
              
              
                =
              
              
                
                  φ
                  
                    hlim
                  
                
                (
                
                  w
                  
                    0
                  
                
                ⋅
                
                  x
                  
                    0
                  
                
                +
                
                  w
                  
                    1
                  
                
                ⋅
                
                  x
                  
                    1
                  
                
                +
                
                  w
                  
                    2
                  
                
                ⋅
                
                  x
                  
                    2
                  
                
                )
                =
                
                  φ
                  
                    hlim
                  
                
                (
                (
                
                  w
                  
                    1
                  
                
                ⋅
                
                  x
                  
                    1
                  
                
                +
                
                  w
                  
                    2
                  
                
                ⋅
                
                  x
                  
                    2
                  
                
                )
                −
                θ
                )
              
            
            
              
              
                =
              
              
                
                  φ
                  
                    hlim
                  
                
                (
                (
                0
                
                  ,
                
                6
                ⋅
                1
                +
                0
                
                  ,
                
                7
                ⋅
                1
                )
                −
                0
                
                  ,
                
                9
                )
                =
                
                  φ
                  
                    hlim
                  
                
                (
                0
                
                  ,
                
                4
                )
                =
                1
              
            
          
        
      
    
    {\displaystyle {\begin{matrix}o&=&\varphi ^{\text{hlim}}(w_{0}\cdot x_{0}+w_{1}\cdot x_{1}+w_{2}\cdot x_{2})=\varphi ^{\text{hlim}}((w_{1}\cdot x_{1}+w_{2}\cdot x_{2})-\theta )\\&=&\varphi ^{\text{hlim}}((0{,}6\cdot 1+0{,}7\cdot 1)-0{,}9)=\varphi ^{\text{hlim}}(0{,}4)=1\end{matrix}}}
  

Für die anderen drei Eingaben, die für das Einlernen mit 
  
    
      
        −
        1
      
    
    {\displaystyle -1}
  
 multipliziert wurden, ergibt sich nun der Wert 
  
    
      
        0
      
    
    {\displaystyle 0}
  
. So folgt aus der Eingabe 
  
    
      
        
          x
          
            1
          
        
        =
        0
      
    
    {\displaystyle x_{1}=0}
  
 und 
  
    
      
        
          x
          
            2
          
        
        =
        1
      
    
    {\displaystyle x_{2}=1}
  
 die Aktivierung:

  
    
      
        o
        =
        
          φ
          
            hlim
          
        
        (
        (
        0
        
          ,
        
        6
        ⋅
        0
        +
        0
        
          ,
        
        7
        ⋅
        1
        )
        −
        0
        
          ,
        
        9
        )
        =
        
          φ
          
            hlim
          
        
        (
        −
        0
        
          ,
        
        2
        )
        =
        0
      
    
    {\displaystyle o=\varphi ^{\text{hlim}}((0{,}6\cdot 0+0{,}7\cdot 1)-0{,}9)=\varphi ^{\text{hlim}}(-0{,}2)=0}
  

Ohne bestimmte Gewichtungen vorzugeben, hat das Neuron gelernt, anhand der Vorgaben die Konjunktion wie im ersten Beispiel darzustellen.

## Anwendungskraft eines einzelnen Neurons

Ein künstliches Neuron ist in der Lage, auch ohne ein gesamtes Netzwerk, maschinell zu lernen. Die statistischen Fachausdrücke sind lineare Regression und Klassifizierung. Damit können lineare Funktionen erlernt und linear trennbare Klassen unterschieden werden. Mithilfe des sogenannten Kerneltricks können aber auch nichtlineare Modelle erlernt werden. Demnach kann ein einzelnes Neuron ähnliche Ergebnisse wie Support Vector Machines erzielen, wenn auch nicht ganz so optimal.
