---
title: Perzeptron
url: https://de.wikipedia.org/wiki/Perzeptron
updated: '2026-06-15T22:56:53Z'
language: de
revision: '267968670'
license: CC BY-SA 4.0
source: Wikipedia
---

Das Perzeptron (nach engl. perception, „Wahrnehmung“) ist ein vereinfachtes künstliches neuronales Netz, das zuerst von Frank Rosenblatt 1957 vorgestellt wurde. Es besteht in der Grundversion (einfaches Perzeptron) aus einem einzelnen künstlichen Neuron mit anpassbaren Gewichtungen und einem Schwellenwert. Unter diesem Begriff werden heute verschiedene Kombinationen des ursprünglichen Modells verstanden, dabei wird zwischen einlagigen und mehrlagigen Perzeptren (engl. multi-layer perceptron, MLP) unterschieden. Perzeptron-Netze wandeln einen Eingabevektor in einen Ausgabevektor um und stellen damit einen einfachen Assoziativspeicher dar.

## Geschichte

1943 führten der Neurophysiologe Warren McCulloch und der Logiker Walter Pitts das „Neuron“ als logisches Schwellwert-Element mit mehreren Eingängen und einem einzigen Ausgang in die Informatik ein. Es konnte als Boolesche Variable die Zustände wahr und falsch annehmen und „feuerte“ (= wahr), wenn die Summe der Eingangssignale einen Schwellenwert überschritt (siehe McCulloch-Pitts-Zelle). Dies entsprach der neurobiologischen Analogie eines Aktionspotentials, das eine Nervenzelle bei einer kritischen Änderung ihres Membranpotentials aussendet. McCulloch und Pitts zeigten, dass durch geeignete Kombination mehrerer solcher Neuronen jede einfache aussagenlogische Funktion (UND, ODER, NICHT) beschreibbar ist.
1949 stellte der Psychologe Donald O. Hebb die Hypothese auf, Lernen beruhe darauf, dass sich die aktivierende oder hemmende Wirkung einer Synapse als Produkt der prä- und postsynaptischen Aktivität berechnen lasse. Es gibt Anhaltspunkte, dass die Langzeit-Potenzierung und das sogenannte spike-timing dependent plasticity (STDP) die biologischen Korrelate des Hebbschen Postulates sind. Überzeugende Evidenz für diese These steht aber noch aus.
1957 schließlich publizierte Frank Rosenblatt das Perzeptron-Modell, das bis heute die Grundlage künstlicher neuronaler Netze darstellt.

### Mark I Perceptron

Das Perceptron war eher als Maschine denn als Programm konzipiert. Obwohl es zunächst als Software für den Großrechner IBM 704 implementiert wurde, wurde es später als „Mark I Perceptron“ unter dem Projektnamen „Project PARA“ in speziell angefertigter Hardware für die Bilderkennung umgesetzt. Die Maschine befindet sich derzeit im National Museum of American History.

Das Mark I Perceptron bestand aus drei Schichten. Eine Version wurde wie folgt implementiert:

Ein Array aus 400 Fotozellen, angeordnet in einem 20×20-Raster, bezeichnet als „Sensor-Einheiten“ (S-Einheiten) oder „Eingangs-Retina“. Jede S-Einheit kann mit bis zu 40 A-Einheiten verbunden werden.
Eine verborgene Schicht aus 512 Perzeptronen, die als „Assoziationseinheiten“ (A-Einheiten) bezeichnet wurden.
Eine Ausgabeschicht aus acht Perzeptronen, die als „Reaktionseinheiten“ (R-Einheiten) bezeichnet wurden.
Rosenblatt nannte dieses dreischichtige Perzeptron-Netzwerk das Alpha-Perzeptron, um es von anderen Perzeptron-Modellen zu unterscheiden, mit denen er experimentierte.
Die S-Einheiten sind über eine Steckplatine zufällig (gemäß einer Zufallszahlentabelle) mit den A-Einheiten verbunden, um „jede bestimmte absichtliche Verzerrung im Perceptron zu beseitigen“. Die Verbindungsgewichte sind fest vorgegeben und werden nicht erlernt. Rosenblatt bestand auf den zufälligen Verbindungen, da er glaubte, dass die Netzhaut zufällig mit dem visuellen Kortex verbunden sei, und er wollte, dass seine Perceptron-Maschine der menschlichen visuellen Wahrnehmung ähnelt.
Die A-Einheiten sind mit den R-Einheiten verbunden, wobei die einstellbaren Gewichte in Potentiometern kodiert sind und die Aktualisierung der Gewichte während des Lernvorgangs durch Elektromotoren erfolgte.  Die Hardware-Details sind in einer Bedienungsanleitung enthalten.
Bei einer von der US-Marine organisierten Pressekonferenz im Jahr 1958 gab Rosenblatt Aussagen zum Perceptron ab, die in der noch jungen KI-Gemeinschaft heftige Kontroversen auslösten. Auf der Grundlage von Rosenblatts Aussagen berichtete die New York Times, das Perceptron sei „der Embryo eines elektronischen Computers, von dem [die Marine] erwartet, dass er gehen, sprechen, sehen, schreiben, sich selbst reproduzieren und sich seiner Existenz bewusst sein wird.“
Die Fotoabteilung der Central Intelligence Agency untersuchte von 1960 bis 1964 den Einsatz der Mark-I-Perceptron-Maschine zur Erkennung militärisch interessanter Silhouetten (wie Flugzeuge und Schiffe) auf Luftbildern.

### Weitere Arbeiten

Rosenblatt setzte seine Arbeit am Perceptron trotz schwindender finanzieller Mittel fort. Der letzte Versuch war „Tobermory“, das zwischen 1961 und 1967 für die Spracherkennung gebaut wurde. Es nahm einen ganzen Raum ein. Es verfügte über vier Schichten mit 12.000 Gewichten, die durch ringförmige Magnetkerne realisiert wurden. Zum Zeitpunkt seiner Fertigstellung waren Simulationen auf digitalen Computern schneller geworden als speziell für diesen Zweck gebaute Perceptron-Maschinen.
Ein Simulationsprogramm für neuronale Netze wurde für den IBM 7090/7094 geschrieben und diente zur Untersuchung verschiedener Anwendungen der Mustererkennung, wie z. B. Zeichenerkennung, Teilchenspuren in Blasenkammeraufnahmen; Phonem-, Einzelwort- und kontinuierliche Spracherkennung; Sprecherverifizierung; sowie Mechanismen zur Erkennung des Fokusbereichs in der Bildverarbeitung.

Der Kernel-Perzeptron-Algorithmus wurde bereits 1964 von Aizerman et al. eingeführt. Margin-Bounds-Garantien für den Perzeptron-Algorithmus im allgemeinen nicht-separierbaren Fall wurden 1998 von Freund und Schapire gegeben. Mohri und Rostamizadeh erweiterten 2013 frühere Ergebnisse und lieferten günstigere L1-Bounds.
Das Perzeptron ist ein vereinfachtes Modell einer biologischen Nervenzelle. Während die Komplexität biologischer Nervenzellmodelle oft erforderlich ist, um das neuronale Verhalten vollständig zu verstehen, deuten Forschungsergebnisse darauf hin, dass ein perzeptronähnliches lineares Modell bestimmte Verhaltensweisen reproduzieren kann, die in realen Nervenzellen zu beobachten sind.
Lösungsräume von Entscheidungsgrenzen für alle binären Funktionen und Lernverhalten wurden ebenfalls untersucht.

## Einlagiges Perzeptron

Beim einlagigen Perzeptron gibt es nur eine einzige Schicht aus künstlichen Neuronen, welche zugleich den Ausgabevektor repräsentiert. Jedes Neuron wird dabei durch eine Neuronenfunktion repräsentiert und erhält den gesamten Eingabevektor als Parameter. Die Verarbeitung erfolgt ganz ähnlich zur sogenannten Hebbschen Lernregel für natürliche Neuronen. Allerdings wird der Aktivierungsfaktor dieser Regel durch eine Differenz zwischen Soll- und Istwert ersetzt. Da die Hebbsche Lernregel sich auf die Gewichtung der einzelnen Eingangswerte bezieht, erfolgt also das Lernen eines Perzeptrons durch die Anpassung der Gewichtung eines jeden Neurons. Sind die Gewichtungen einmal gelernt, so ist ein Perzeptron auch in der Lage, Eingabevektoren zu klassifizieren, die vom ursprünglich gelernten Vektor leicht abweichen. Gerade darin besteht die gewünschte Klassifizierungsfähigkeit des Perzeptrons, der es seinen Namen verdankt.

### Berechnung der Ausgabewerte

Mit einem Bias 
  
    
      
        b
      
    
    {\displaystyle b}
  
, den Eingaben 
  
    
      
        
          x
          
            i
          
        
      
    
    {\displaystyle x_{i}}
  
 und den Gewichten 
  
    
      
        
          w
          
            i
            j
          
        
      
    
    {\displaystyle w_{ij}}
  
 berechnen sich die Ausgabewerte 
  
    
      
        
          o
          
            j
          
        
      
    
    {\displaystyle o_{j}}
  
 zu

  
    
      
        
          o
          
            j
          
        
        =
        
          
            {
            
              
                
                  1
                
                
                  
                    ∑
                    
                      i
                    
                  
                  
                    w
                    
                      i
                      j
                    
                  
                  
                    x
                    
                      i
                    
                  
                  +
                  b
                  >
                  0
                
              
              
                
                  0
                
                
                  
                    ansonsten
                  
                
              
            
            
          
        
      
    
    {\displaystyle o_{j}={\begin{cases}1&\sum _{i}w_{ij}x_{i}+b>0\\0&{\text{ansonsten}}\end{cases}}}
  
.
Anmerkungen

Der Bias 
  
    
      
        b
      
    
    {\displaystyle b}
  
 ist als Schwellenwert 
  
    
      
        θ
      
    
    {\displaystyle \theta }
  
 (engl. threshold) mit einem negativen Vorzeichen festgelegt.
Verwendet man stattdessen den Schwellenwert 
  
    
      
        θ
      
    
    {\displaystyle \theta }
  
, so ergibt sich die erste Bedingung  zu 
  
    
      
        
          ∑
          
            i
          
        
        
          w
          
            i
            j
          
        
        
          x
          
            i
          
        
        >
        θ
      
    
    {\displaystyle \sum _{i}w_{ij}x_{i}>\theta }
  
 und es ändert sich auch beim zugehörigen Funktionsterm das entsprechende Vorzeichen.

### Perzeptron-Lernregel

Es gibt verschiedene Versionen der Lernregel, um auf die unterschiedlichen Definitionen des Perzeptrons einzugehen. Für ein Perzeptron mit binären Ein- und Ausgabewerten wird hier die Lernregel angegeben. Diese Regel konvergiert nur, wenn der Trainings-Datensatz linear separierbar ist, siehe dazu unten unter "Varianten".
Folgende Überlegungen liegen der Lernregel des Perzeptrons zu Grunde:

Wenn die Ausgabe eines Neurons 1 (bzw. 0) ist und den Wert 1 (bzw. 0) annehmen soll, dann werden die Gewichtungen nicht geändert.
Ist die Ausgabe 0, soll aber den Wert 1 annehmen, dann werden die Gewichte inkrementiert.
Ist die Ausgabe 1, soll aber den Wert 0 annehmen, dann werden die Gewichte dekrementiert.
Mathematisch wird der Sachverhalt folgendermaßen ausgedrückt:

  
    
      
        
          w
          
            i
            j
          
          
            
              n
              e
              u
            
          
        
        =
        
          w
          
            i
            j
          
          
            
              a
              l
              t
            
          
        
        +
        Δ
        
          w
          
            i
            j
          
        
      
    
    {\displaystyle w_{ij}^{\mathrm {neu} }=w_{ij}^{\mathrm {alt} }+\Delta w_{ij}}
  
,

  
    
      
        Δ
        
          w
          
            i
            j
          
        
        =
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
          
        
      
    
    {\displaystyle \Delta w_{ij}=\alpha \cdot (t_{j}-o_{j})\cdot x_{i}}
  
.
Dabei ist

  
    
      
        Δ
        
          w
          
            i
            j
          
        
      
    
    {\displaystyle \Delta w_{ij}}
  
 die Änderung des Gewichts 
  
    
      
        
          w
          
            i
            j
          
        
      
    
    {\displaystyle w_{ij}}
  
 für die Verbindung zwischen der Eingabezelle 
  
    
      
        i
      
    
    {\displaystyle i}
  
 und Ausgabezelle 
  
    
      
        j
      
    
    {\displaystyle j}
  
,

  
    
      
        
          t
          
            j
          
        
      
    
    {\displaystyle t_{j}}
  
 die gewünschte Ausgabe des Neurons 
  
    
      
        j
      
    
    {\displaystyle j}
  
,

  
    
      
        
          o
          
            j
          
        
      
    
    {\displaystyle o_{j}}
  
 die tatsächliche Ausgabe,

  
    
      
        
          x
          
            i
          
        
      
    
    {\displaystyle x_{i}}
  
 die Eingabe des Neurons 
  
    
      
        i
      
    
    {\displaystyle i}
  
 und

  
    
      
        α
        >
        0
      
    
    {\displaystyle \alpha >0}
  
 die Lernrate.
Eine Gewichtsaktualisierung im Schritt 
  
    
      
        k
      
    
    {\displaystyle k}
  
 verläuft danach wie folgt:

  
    
      
        
          w
          
            i
            j
          
        
        (
        k
        +
        1
        )
        =
        
          w
          
            i
            j
          
        
        (
        k
        )
      
    
    {\displaystyle w_{ij}(k+1)=w_{ij}(k)}
  
 bei korrekter Ausgabe,

  
    
      
        
          w
          
            i
            j
          
        
        (
        k
        +
        1
        )
        =
        
          w
          
            i
            j
          
        
        (
        k
        )
        +
        α
        
          x
          
            i
          
        
      
    
    {\displaystyle w_{ij}(k+1)=w_{ij}(k)+\alpha x_{i}}
  
 bei Ausgabe 0 und gewünschter Ausgabe 1 und

  
    
      
        
          w
          
            i
            j
          
        
        (
        k
        +
        1
        )
        =
        
          w
          
            i
            j
          
        
        (
        k
        )
        −
        α
        
          x
          
            i
          
        
      
    
    {\displaystyle w_{ij}(k+1)=w_{ij}(k)-\alpha x_{i}}
  
 bei Ausgabe 1 und gewünschter Ausgabe 0.
Rosenblatt konnte im Konvergenztheorem nachweisen, dass mit dem angegebenen Lernverfahren alle Lösungen eingelernt werden können, die ein Perzeptron repräsentieren kann.

### XOR-Problem

Frank Rosenblatt zeigte, dass ein einfaches Perzeptron mit zwei Eingabewerten und einem einzigen Ausgabeneuron zur Darstellung der einfachen logischen Operatoren AND, OR und NOT genutzt werden kann. Marvin Minsky und Seymour Papert wiesen jedoch 1969 nach, dass ein einlagiges Perzeptron den XOR-Operator nicht auflösen kann (Problem der linearen Separierbarkeit). Dies führte zu einem Stillstand in der Forschung der künstlichen neuronalen Netze.
Die in diesem Zusammenhang zum Teil äußerst polemisch geführte Diskussion war letztlich ein Richtungsstreit zwischen den Vertretern der symbolischen künstlichen Intelligenz und der „Konnektionisten“ um Forschungsgelder. Frank Rosenblatt hatte zwar gezeigt, dass der logische Operator XOR durch die Verwendung eines mehrlagigen Perzeptrons beschrieben werden kann, was sich aus der Äquivalenz zur folgenden Kombination der Operatoren OR, AND und NOT ergibt: 
  
    
      
        (
        A
        ∨
        B
        )
        ∧
        ¬
        (
        A
        ∧
        B
        )
      
    
    {\displaystyle (A\vee B)\wedge \neg (A\wedge B)}
  
. Er starb jedoch zu früh, um sich gegen die Angriffe seiner KI-Kollegen zu wehren.

### Varianten der Perzeptron-Lernregel

Die oben angegebene Standard-Lernregel konvergiert nur, wenn der Trainings-Datensatz linear separierbar ist. Ist dies nicht der Fall, so wird die Standard-Lernregel keine approximative Lösung erzeugen (zum Beispiel eine Lösung mit möglichst wenigen falsch zugeordneten Daten).  Stattdessen wird der Lernvorgang vollständig versagen.
Da lineare Separierbarkeit des Trainings-Datensatzes oft nicht vor Trainingsbeginn bekannt ist, sollten daher Varianten des Trainingsalgorithmus benutzt werden, die robust sind in dem Sinne, dass sie im nicht linear separablen Fall zu einer approximativen Lösung konvergieren.
Ein solches robustes Verfahren ist der Maxover-Algorithmus. Im linear separablen Fall löst er das Trainingsproblem vollständig, auch unter weiteren Optimierungsbedingungen wie maximaler Stabilität (maximaler Abstand zwischen den Daten mit Ausgabe 0 und 1). Im nicht linear separablen Fall erzeugt er eine Lösung mit wenigen falsch zugeordneten Daten. In beiden Fällen geschieht eine graduelle Annäherung an die Lösung im Laufe des Lernvorganges. Der Algorithmus konvergiert zu einer global optimalen Lösung im linear separablen Fall, bzw. zu einer lokal optimalen Lösung im nicht linear separablen Fall.
Der Pocket-Algorithmus lernt mit einer Standard-Perzeptron-Lernregel. Er behält diejenige Lösung, die bisher die wenigsten falsch zugeordneten Daten produzierte, in seiner „Tasche“ (pocket), und gibt diese als approximative Lösung aus.
Im linear separablen Fall lernt dieser Algorithmus vollständig. Im nicht linear separablen Fall wird ausgenutzt, dass die Standard-Perzeptron-Lernregel zufällige Lösungen produziert, unter denen stochastisch solche approximativen Lösungen auftauchen. Der  Pocket-Algorithmus hat somit Nachteile:
Zum einen erfolgt keine graduelle Annäherung an die Lösung, sondern stochastische Sprünge werden ausgenutzt. Da diese zu unvorhersehbaren Zeitpunkten im Lernvorgang auftreten, gibt es keine Sicherheit darüber, wie weit sich der Algorithmus nach einer bestimmten Anzahl von Lernschritten einer optimalen Lösung angenähert hat. Zum anderen muss in jedem Lernschritt die Gesamtzahl der richtig zugeordneten Daten ermittelt werden. Der Algorithmus arbeitet also nicht lokal, wie für neuronale Netze typisch.
Ist die lineare Separabilität des Trainingsdatensatzes bekannt, so können verschiedene Varianten der Standard-Perzeptron-Lernregel genutzt werden. Das "Perzeptron der optimalen Stabilität" (maximaler Abstand zwischen den Daten mit Ausgabe "0" und "1") kann erzeugt werden mit dem Min-Over-Algorithmus (Krauth und Mezard, 1987). Ein besonders schneller Algorithmus, der auf quadratischer Optimierung basiert, ist das AdaTron (Anlauf and Biehl, 1989) Optimale Stabilität, zusammen mit dem Kernel-Trick,  sind die konzeptuellen Voraussetzungen der Support Vector Machine.

### Das Perzeptron als linearer Klassifikator

Jenseits aller (pseudo-)biologischen Analogien ist ein einlagiges Perzeptron letztlich nichts weiter als ein linearer Klassifikator der Form 
  
    
      
        x
        =
        
          a
          
            1
          
        
        
          y
          
            1
          
        
        +
        
          a
          
            2
          
        
        
          y
          
            2
          
        
        +
        ⋯
        +
        
          a
          
            n
          
        
        
          y
          
            n
          
        
      
    
    {\displaystyle x=a_{1}y_{1}+a_{2}y_{2}+\cdots +a_{n}y_{n}}
  
 (lineare Diskriminanzfunktion, multiple lineare Regression). In der Nomenklatur der künstlichen neuronalen Netze werden 
  
    
      
        
          a
          
            1
          
        
      
    
    {\displaystyle a_{1}}
  
 bis 
  
    
      
        
          a
          
            n
          
        
      
    
    {\displaystyle a_{n}}
  
 als Gewichte und 
  
    
      
        
          y
          
            1
          
        
      
    
    {\displaystyle y_{1}}
  
 bis 
  
    
      
        
          y
          
            n
          
        
      
    
    {\displaystyle y_{n}}
  
 als Eingangssignale bezeichnet, wobei letztere nur Werte von 1 oder 0 („wahr“ oder „falsch“) annehmen können. Überschreitet die Summe 
  
    
      
        x
      
    
    {\displaystyle x}
  
 einen Schwellenwert, so wird die Zuordnung der gesuchten Klasse auf „wahr“ bzw. 1 gesetzt, sonst auf „falsch“ bzw. 0.

## Mehrlagiges Perzeptron

Die Beschränkung des einlagigen Perzeptrons konnte später mit dem mehrlagigen Perzeptron (Multi-Layer-Perzeptron) gelöst werden, bei dem es neben der Ausgabeschicht auch noch mindestens eine weitere Schicht verdeckter Neuronen gibt (engl. hidden layer). Sind die Ausgänge nur mit Eingängen einer nachfolgenden Schicht verknüpft, so dass der Informationsfluss nur in einer Richtung verläuft, spricht man von Feed-forward-Netzen. Dabei haben sich folgende Topologien bewährt:

Fully connected: Die Neuronen einer Schicht werden mit allen Neuronen der direkt folgenden Schicht verbunden.
Short-Cuts: Einige Neuronen sind nicht nur mit allen Neuronen der nächsten Schicht verbunden, sondern darüber hinaus mit weiteren Neuronen der übernächsten Schichten.
Sind im Netz Neuronen vorhanden, deren Ausgänge mit Neuronen derselben oder einer vorangegangenen Schicht verbunden sind, handelt es sich um ein rekurrentes neuronales Netz.
Mehrlagige Perzeptronen benötigen komplexere Lernregeln als einlagige Perzeptronen. Backpropagation ist ein möglicher Algorithmus für überwachtes Lernen.
Die Erweiterung dieser Netztopologien um weitere verborgene Schichten und Einführung anderer Architekturen (zum Beispiel rekurrente neuronale Netze), die ebenfalls meist mittels backpropagation trainiert werden, wird heute unter dem Schlagwort Deep Learning zusammengefasst.
