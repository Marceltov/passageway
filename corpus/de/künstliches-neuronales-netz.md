---
title: Künstliches neuronales Netz
url: https://de.wikipedia.org/wiki/K%C3%BCnstliches_neuronales_Netz
updated: '2026-10-25T22:41:40Z'
language: de
revision: '271629840'
license: CC BY-SA 4.0
source: Wikipedia
---

Künstliche neuronale Netze, auch künstliche neuronale Netzwerke, kurz: KNN (englisch artificial neural network, ANN), sind Netze aus künstlichen Neuronen, deren Aufbau von den Netzwerken biologischer Neuronen in Gehirnen inspiriert wurde. Die künstlichen Neuronen in einem KNN sind miteinander verbunden und in der Regel in Schichten organisiert.
KNN werden beim maschinellen Lernen eingesetzt. Damit können spezielle Probleme mittels Computern gelöst werden, die zu kompliziert sind, um sie mit Regeln zu beschreiben, zu denen es aber viele Daten gibt, die als Beispiele für die gewünschte Lösung dienen können.
KNN bilden die Basis für Deep Learning, das ab etwa 2006 erhebliche Fortschritte bei der Analyse von großen Datenmengen erlaubte. Erfolgreiche Anwendungen des Deep Learning sind beispielsweise Bilderkennung und Spracherkennung.
KNNs sind Forschungsgegenstand sowohl des Maschinellen Lernens/Deep Learnings, das ein Teilbereich der künstlichen Intelligenz (KI) ist, als auch der interdisziplinären Neuroinformatik. Das Nachbilden eines aus Neuronen aufgebauten biologischen neuronalen Netzes ist eher Gegenstand der Computational Neuroscience.

## Überblick

KNN werden beim maschinellen Lernen eingesetzt. Damit können Computer Probleme lösen, die zu kompliziert sind, um sie mit Regeln zu beschreiben, zu denen es aber viele Daten gibt, die als Beispiele für die gewünschte Lösung dienen können. Ein Algorithmus passt das zunächst unwissende Netz so an die Beispieldaten an, dass es von ihnen auf neue Fälle verallgemeinern kann. Dieser Vorgang wird Training genannt. Das trainierte Netz kann für neue Daten Vorhersagen treffen oder Empfehlungen und Entscheidungen erzeugen.
KNN wurden von den Netzwerken inspiriert, die biologische Neuronen in Gehirnen bilden. Biologische Neuronen sind miteinander vernetzt und in Schichten organisiert. Sie können mehrere Eingangssignale aufsummieren und geben nur dann ein Signal an andere Neuronen weiter, wenn die Summe der Eingangssignale einen Schwellenwert erreicht.
Ein KNN wird von künstlichen Neuronen gebildet. Künstliche Neuronen bilden ausgewählte Eigenschaften von biologischen Neuronen mit mathematischen Mitteln nach. Ein künstliches Neuron kann mehrere Eingangssignale aufsummieren. Jedes Eingangssignal wird gewichtet und kann dadurch die Summe der Eingangssignale unterschiedlich stark erhöhen oder reduzieren. Die Aktivierungsfunktion eines künstlichen Neurons sorgt dafür, dass es nur dann ein Ausgangssignal ausgibt, wenn die Summe aller Eingangssignale einen Schwellenwert überschreitet. Wenn die Summe aller Eingangssignale unter dem Schwellenwert liegt, gibt das künstliche Neuron kein Ausgangssignal aus.
In der Regel besteht ein KNN aus mehreren Schichten von künstlichen Neuronen. Die Signale wandern von der ersten Schicht (der Eingabeschicht) zur letzten Schicht (der Ausgabeschicht) und durchlaufen dabei möglicherweise mehrere Zwischenschichten (versteckte Schichten). Jede Schicht kann die Signale an ihren Eingängen unterschiedlich transformieren. Ein Netz mit vielen verborgenen Schichten kann eine komplizierte Aufgabe in mehrere einfachere Aufgaben zerlegen, die jeweils in verschiedenen Schichten des Modells ausgeführt werden. Ein solches KNN wird auch als tiefes neuronales Netz bezeichnet. Darauf bezieht sich der Begriff „Deep Learning“.
Zu Beginn des Trainings stehen alle Schwellenwerte und Gewichte auf Zufallswerten. Während des Trainings passt ein Algorithmus schrittweise Schwellenwerte und Gewichte an die Daten an, mit denen das Netz trainiert wird, siehe auch Optimierung. Die resultierenden Gewichte werden als Parameter des KI-Modells bezeichnet. Das Training wird beendet, wenn das Netz für alle Beispiele aus den Trainingsdaten eine möglichst korrekte Ausgabe erzeugt.
Das Erstellen eines geeigneten Trainingsdatensatzes kann sehr schwierig sein, da man verhindern muss, dass die Daten Muster aufweisen, die das Netz nicht zur Entscheidung heranziehen soll. Das Forschungsgebiet Explainable Artificial Intelligence arbeitet an Verfahren, die erklären können, wie ein trainiertes KNN zu einer Entscheidung kommt. Beispielsweise wurde untersucht, welchen Teil eines Bildes ein KNN betrachtet, um ein Bild zu klassifizieren. Dabei entdeckten die Forscher z. B. ein KNN, das Eisenbahnzüge erkennen sollte und dazu nur auf Schienen achtete.

## Beschreibung

Künstliche neuronale Netze basieren meist auf der Vernetzung vieler McCulloch-Pitts-Neuronen oder leichter Abwandlungen davon. Die Topologie eines Netzes (die Zuordnung von Verbindungen zu Knoten) muss im Hinblick auf seine Aufgabe gut durchdacht sein. Nach der Konstruktion eines Netzes folgt die Trainingsphase, in der das Netz „lernt“. Theoretisch kann ein Netz durch folgende Methoden lernen:

Entwicklung neuer Verbindungen
Löschen existierender Verbindungen
Ändern der Gewichtung (der Gewichte der Verbindung 
  
    
      
        
          w
          
            i
            j
          
        
      
    
    {\displaystyle w_{ij}}
  
 von Neuron 
  
    
      
        j
      
    
    {\displaystyle j}
  
 zu Neuron 
  
    
      
        i
      
    
    {\displaystyle i}
  
)
Anpassen der Schwellenwerte der Neuronen, sofern diese Schwellenwerte besitzen
Hinzufügen oder Löschen von Neuronen
Modifikation von Aktivierungs-, Propagierungs- oder Ausgabefunktion
Außerdem verändert sich das Lernverhalten bei Veränderung der Aktivierungsfunktion der Neuronen oder der Lernrate des Netzes. Praktisch gesehen „lernt“ ein Netz hauptsächlich durch Modifikation der Gewichte der Verbindungen zwischen den Neuronen. Eine Anpassung des Schwellenwertes kann hierbei durch ein on-Neuron miterledigt werden. Dadurch sind KNNs in der Lage, komplizierte nichtlineare Funktionen über einen „Lern“-Algorithmus, der durch iterative oder rekursive Vorgehensweise aus vorhandenen Ein- und gewünschten Ausgangswerten alle Parameter der Funktion zu bestimmen versucht, zu erlernen. KNNs sind dabei eine Realisierung des konnektionistischen Paradigmas, da die Funktion aus vielen einfachen gleichartigen Teilen besteht. Erst in ihrer Summe kann deren Verhalten im Zusammenspiel sehr vieler beteiligter Teile komplex werden. Ein neuronales Netz, das deterministisch beschrieben wird und Rückkopplungen erlaubt, stellt unter dem Gesichtspunkt der Berechenbarkeit ein äquivalentes Modell zur Turingmaschine dar. D.h. zu jedem Netz gibt es mindestens eine Turingmaschine und zu jeder Turingmaschine gibt es mindestens ein Netz mit Rückkopplung. Bei einer stochastischen Beschreibung ist dies nicht der Fall. Rekurrente Netze sind damit die ausdrucksstärkste Form (Typ 0 in der Chomsky-Hierarchie).

## Geschichtliche Entwicklung

Das Interesse für künstliche neuronale Netze setzte bereits in den frühen 1940er Jahren ein, also etwa gleichzeitig mit dem Einsatz programmierbarer Computer in angewandter Mathematik.

### Anfänge

Die Anfänge gehen auf Warren McCulloch und Walter Pitts zurück. Sie beschrieben 1943 Verknüpfungen von elementaren Einheiten zu einem Netz ähnlich dem der Neuronen im Gehirn, mit dem sich praktisch jede logische oder arithmetische Funktion berechnen lassen könnte. 1947 wiesen sie darauf hin, dass ein solches Netz beispielsweise zur räumlichen Mustererkennung eingesetzt werden kann. 1949 formulierte Donald O. Hebb seine Hebbsche Lernregel, die in ihrer allgemeinen Form die meisten der künstlichen neuronalen Lernverfahren wiedergibt. Karl Lashley fand 1950, dass der Prozess der Informationsspeicherung im Gehirn verteilt auf verschiedene Untereinheiten realisiert wird.

### Erste Blütezeit

Im anschließenden Jahr, 1951, gelingt Marvin Minsky mit seiner Dissertationsarbeit der Bau des Neurocomputers Snarc, der seine Gewichte automatisch justieren kann, jedoch nicht praktisch einsetzbar ist. 1956 treffen sich Wissenschaftler und Studenten auf der Dartmouth Conference. Diese Konferenz gilt als Geburtsstunde der Künstlichen Intelligenz als akademisches Fachgebiet. Von 1957 bis 1958 entwickeln Frank Rosenblatt und Charles Wightman den ersten erfolgreichen Neurocomputer, mit dem Namen Mark I Perceptron. Der Computer konnte mit seinem 20 × 20 Pixel großen Bildsensor bereits einfache Ziffern erkennen. Im nachfolgenden Jahr formuliert Rosenblatt das Perceptron-Konvergenz-Theorem. 1960 stellen Bernard Widrow und Marcian E. Hoff das ADALINE (ADAptive LInear NEuron) vor. Dieses Netz erreichte als erstes weite kommerzielle Verbreitung. Anwendung fand es in Analogtelefonen zur Echtzeit-Echofilterung. Das neuronale Netz lernte mit der Deltaregel. 1961 stellte Karl Steinbuch Techniken der assoziativen Speicherung vor. 1969 gaben Marvin Minsky und Seymour Papert eine genaue mathematische Analyse des Perceptrons. Sie zeigten auf, dass wichtige Probleme nicht gelöst werden können. So sind unter anderem XOR-Operatoren nicht auflösbar und es gibt Probleme in der linearen Separierbarkeit. Die Folge war ein vorläufiges Ende der Forschungen auf dem Gebiet der neuronalen Netze, da die meisten Forschungsgelder gestrichen wurden.

### Langsamer Wiederaufbau

1972 präsentiert Teuvo Kohonen den linearen Assoziator, ein Modell des Assoziativspeichers. James A. Anderson beschreibt das Modell unabhängig von Kohonen aus neuropsychologischer Sicht im selben Jahr. 1973 benutzt Christoph von der Malsburg ein Neuronenmodell, das nichtlinear ist. Bereits 1974 entwickelt Paul Werbos für seine Dissertation die Backpropagation bzw. die Fehlerrückführung. Das Modell bekam aber erst später eine größere Bedeutung. Ab 1976 entwickelt Stephen Grossberg mathematisch fundierte Modelle neuronaler Netze. Zusammen mit Gail Carpenter widmet er sich auch dem Problem, ein neuronales Netz lernfähig zu halten, ohne bereits Gelerntes zu zerstören. Sie formulieren ein Architekturkonzept für neuronale Netze, die Adaptive Resonanztheorie. 1982 beschreibt Teuvo Kohonen die nach ihm benannten selbstorganisierenden Karten. Im selben Jahr beschreibt John Hopfield das Modell der Hopfield-Netze. 1983 wird von Kunihiko Fukushima, S. Miyake und T. Ito das neuronale Modell Neocognitron vorgestellt. Das Modell war eine Weiterentwicklung des 1975 entwickelten Cognitrons und diente zur Erkennung handgeschriebener Zeichen.

### Renaissance

1985 veröffentlicht John Hopfield eine Lösung des Travelling Salesman Problems durch ein Hopfield-Netz. 1985 wird das Lernverfahren Backpropagation of Error als Verallgemeinerung der Delta-Regel durch die Parallel-Distributed-Processing-Gruppe separat entwickelt. Somit werden nicht linear separierbare Probleme durch mehrschichtige Perceptrons lösbar. Marvin Minskys Auffassung war also widerlegt.

### Neue Erfolge in Mustererkennungswettbewerben seit 2009

In jüngster Zeit erlebten neuronale Netze eine Wiedergeburt, da sie bei herausfordernden Anwendungen oft bessere Ergebnisse als konkurrierende Lernverfahren liefern. Zwischen 2009 und 2012 gewannen die rekurrenten bzw. tiefen vorwärtsgerichteten neuronalen Netze der Forschungsgruppe von Jürgen Schmidhuber am Schweizer KI Labor IDSIA eine Serie von acht internationalen Wettbewerben in den Bereichen Mustererkennung und maschinelles Lernen. Insbesondere gewannen ihre rekurrenten LSTM-Netze drei Wettbewerbe zur verbundenen Handschrifterkennung bei der Intl. Conf. on Document Analysis and Recognition (ICDAR) 2009 – obwohl kein A-priori-Wissen über die drei verschiedenen zu lernenden Sprachen in die Programmierung der Modelle einbezogen wurde. Die LSTM-Netze erlernten gleichzeitige Segmentierung und Erkennung. Dies waren die ersten internationalen Wettbewerbe, die durch Deep Learning oder durch rekurrente Netze gewonnen wurden.
Tiefe vorwärtsgerichtete Netze wie Kunihiko Fukushimas Konvolutionsnetz der 80er Jahre haben wieder an Bedeutung gewonnen. Sie verfügen über alternierende Konvolutionslagen (convolutional layers) und Lagen von Neuronen, die mehrere Aktivierungen zusammenfassen (pooling layers), um die räumliche Dimension zu reduzieren. Abgeschlossen wird ein solches Konvolutionsnetz in der Regel durch mehrere vollständig verbundene Schichten (englisch fully connected layers). Yann LeCuns Team von der New York University wandte den 1989 schon gut bekannten Backpropagation-Algorithmus auf solche Netze an. Moderne Varianten verwenden sogenanntes max-pooling für die Zusammenfassung der Aktivierungen, das stets der stärksten Aktivierung den Vorzug gibt. Schnelle Grafikprozessor (GPU)-Implementierungen dieser Kombination wurden 2011 durch Dan Ciresan und Kollegen in Schmidhubers Gruppe eingeführt. Sie gewannen seither zahlreiche Wettbewerbe, u. a. die „ISBI 2012 Segmentation of Neuronal Structures in Electron Microscopy Stacks Challenge“ und den „ICPR 2012 Contest on Mitosis Detection in Breast Cancer Histological Images“. AlexNet, ein ähnliches Modell, erzielte auch die zu diesem Zeitpunkt besten Ergebnisse auf dem ImageNet Benchmark. GPU-basierte max-pooling-Konvolutionsnetze waren auch die ersten künstlichen Mustererkenner mit übermenschlicher Performanz in Wettbewerben wie der „IJCNN 2011 Traffic Sign Recognition Competition“. In den letzten Jahren fand auch die Theorie der Zufallsmatrizen vermehrt Anwendung in der Erforschung von neuronalen Netzen. Neuronale Operatoren sind Verallgemeinerungen von künstlichen neuronalen Netzwerken auf unendlichdimensionale Funktionenräume. Die primäre Anwendung von neuronalen Operatoren liegt darin Lösungsoperatoren von partiellen Differentialgleichungen zu erlernen.

## Topologie der Verbindungsnetze

In künstlichen neuronalen Netzen bezeichnet die Topologie die Struktur des Netzes. Damit ist im Allgemeinen gemeint, wie viele künstliche Neuronen sich auf wie vielen Schichten befinden, und wie diese miteinander verbunden sind. Künstliche Neuronen können auf vielfältige Weise zu einem künstlichen neuronalen Netz verbunden werden. Dabei werden Neuronen bei vielen Modellen in hintereinander liegenden Schichten (englisch layers) angeordnet; bei einem Netz mit nur einer trainierbaren Neuronenschicht spricht man von einem einschichtigen Netz.
Unter Verwendung eines Graphen können die Neuronen als Knoten und ihre Verbindungen als Kanten dargestellt werden. Die Eingaben werden gelegentlich auch als Knoten dargestellt, was hilft, den Informationsfluss durch das Netzwerk zu visualisieren.
Die hinterste Schicht des Netzes, deren Neuronenausgaben meist als einzige außerhalb des Netzes sichtbar sind, wird Ausgabeschicht (englisch output layer) genannt. Davorliegende Schichten werden entsprechend als versteckte Schicht (englisch hidden layer) bezeichnet.

### Typische Strukturen

Die Struktur eines Netzes hängt unmittelbar mit dem verwendeten Lernverfahren zusammen und umgekehrt; so kann mit der Delta-Regel nur ein einschichtiges Netz trainiert werden, bei mehreren Schichten ist eine leichte Abwandlung vonnöten. Dabei müssen Netze nicht zwingend homogen sein: es existieren auch Kombinationen aus verschiedenen Modellen, um so unterschiedliche Vorteile zu kombinieren.
Es gibt reine feedforward-Netze, bei denen eine Schicht immer nur mit der nächsthöheren Schicht verbunden ist. Darüber hinaus gibt es Netze, in denen Verbindungen in beiden Richtungen erlaubt sind. Die passende Netzstruktur wird meist nach der Methode von Versuch und Irrtum gefunden, was durch evolutionäre Algorithmen und eine Fehlerrückführung unterstützt werden kann.

#### Einschichtiges feedforward-Netz

Einschichtige Netze mit der feedforward-Eigenschaft (englisch für vorwärts) sind die einfachsten Strukturen künstlicher neuronaler Netze. Sie besitzen lediglich eine Ausgabeschicht. Die feedforward-Eigenschaft besagt, dass Neuronenausgaben nur in Verarbeitungsrichtung geleitet werden und nicht durch eine rekurrente Kante zurückgeführt werden können (azyklischer, gerichteter Graph).

#### Mehrschichtiges feedforward-Netz

Mehrschichtige Netze besitzen neben der Ausgabeschicht auch verdeckte Schichten, deren Ausgabe wie beschrieben, außerhalb des Netzes nicht sichtbar sind. Verdeckte Schichten verbessern die Abstraktion solcher Netze. So kann erst das mehrschichtige Perzeptron das XOR-Problem lösen.

#### Rekurrentes Netz

Rekurrente Netze besitzen im Gegensatz dazu auch rückgerichtete (rekurrente) Kanten (englisch feedback loops) und enthalten somit eine Rückkopplung. Solche Kanten werden dann immer mit einer Zeitverzögerung (in der Systemtheorie als Verzögerungsglied bezeichnet) versehen, sodass bei einer schrittweisen Verarbeitung die Neuronenausgaben der vergangenen Einheit wieder als Eingaben angelegt werden können. Diese Rückkopplungen ermöglichen einem Netz ein dynamisches Verhalten und statten es mit einem Gedächtnis aus.

#### Dynamische neuronale Netze

Dynamische neuronale Netze passen die Struktur und/oder Parameter dynamisch je nach Input bei der Inferenz an.

#### Neuronale Netze mit Gedächtnis

Neuronale Netze mit Gedächtnis verfügen über einen statischen Speicher, der bei der Inferenz dynamisch abgefragt werden kann.

## Funktionsweise

Künstliche neuronale Netze dienen als universelle Funktionsapproximatoren. Werte werden dabei von der Eingabe- bis zur Ausgabeschicht propagiert, wobei eine Aktivierungsfunktion für Nichtlinearität sorgt. Beim Trainieren wird ein Fehler bestimmt; mit Hilfe von Fehlerrückführung und einem Optimierungsverfahren werden dabei die Gewichte schichtweise angepasst.

### Künstliche Neuronen

Ein künstliches Neuron erhält Eingaben von anderen Neuronen (oder von außen), wie auf dem Bild rechts zu erkennen ist. Der Wert einer Eingabe hängt vom Aktivitätslevel des sendenden Neurons und vom Gewicht 
  
    
      
        
          w
          
            i
            j
          
        
      
    
    {\displaystyle w_{ij}}
  
 der Verbindung zwischen Sender- und Empfänger-Neuron ab.
Die Propagierungsfunktion (Übertragungsfunktion) errechnet aus den einzelnen Eingaben und ihren Gewichten die Gesamteingabe 
  
    
      
        n
        e
        
          t
          
            j
          
        
      
    
    {\displaystyle net_{j}}
  
 für das Neuron, die Netz-Eingabe oder Netz-Input genannt wird. Am häufigsten wird die gewichtete Summe (Linearkombination) verwendet:

  
    
      
        
          
            
              net
            
          
          
            j
          
        
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
            j
          
        
        .
      
    
    {\displaystyle {\mbox{net}}_{j}=\sum \limits _{i=1}^{n}x_{i}w_{ij}.}
  

Welches Aktivitätslevel 
  
    
      
        
          o
          
            j
          
        
      
    
    {\displaystyle o_{j}}
  
 das Neuron annimmt, wird nicht direkt durch die Netz-Eingabe bestimmt, sondern durch die Aktivierungsfunktion. Dieses Aktivitätslevel bestimmt dann die Ausgabe des Neurons an Neuronen der nächsten Schicht.

  
    
      
        
          o
          
            j
          
        
        =
        φ
        (
        
          
            
              net
            
          
          
            j
          
        
        )
      
    
    {\displaystyle o_{j}=\varphi ({\mbox{net}}_{j})}
  

Die Aktivierungsfunktion ermöglicht die Einführung von Nichtlinearität ins neuronale Netz, denn nicht alle Aufgaben neuronaler Netze lassen sich mit linearen Funktionen abbilden. Es gibt verschiedene Aktivierungsfunktionen. In den verdeckten Schichten wird meist die Rectifier-Funktion verwendet, in der Ausgabeschicht eine Sigmoidfunktion.
Hierbei ist

  
    
      
        φ
      
    
    {\displaystyle \varphi }
  
 eine differenzierbare Funktion, deren Ableitung nicht überall gleich null ist,

  
    
      
        n
      
    
    {\displaystyle n}
  
 die Anzahl der Eingaben,

  
    
      
        
          x
          
            i
          
        
      
    
    {\displaystyle x_{i}}
  
 die von Neuron 
  
    
      
        i
      
    
    {\displaystyle i}
  
 kommende Eingabe

  
    
      
        
          w
          
            i
            j
          
        
      
    
    {\displaystyle w_{ij}}
  
 die Gewichtung im Neuron 
  
    
      
        j
      
    
    {\displaystyle j}
  
 für die Eingabe 
  
    
      
        
          x
          
            i
          
        
      
    
    {\displaystyle x_{i}}
  
.
Die Aktivierungsfunktion, welche im allerletzten Schritt des neuronalen Netzes ausgeführt wird, kann als Ausgabefunktion aufgefasst werden. Diese Ausgabefunktion hat als Hauptaufgabe sicherzustellen, dass der Bereich (Träger) der Ausgaben zu weiteren Annahmen der Modellierung passt. Die Ausgabefunktion kann sicherstellen, dass Verteilungsvoraussetzungen der Likelihoodfunktion erfüllt sind, wie z. B. die Ausgabe von strikt positiven Ergebnissen oder Ergebnissen nur im Intervall von 0 bis 1. Die Aufgabe der Ausgabefunktion ist direkt analog zur (inversen) Linkfunktion in verallgemeinerten linearen Modellen.

### Verlustfunktion

Mit Hilfe von verbundenen Neuronen, die die Propagierungs- und Aktivierungsfunktionen anwenden, gibt das neuronale Netz einen Zahlenvektor aus. Inwieweit das Ergebnis aus dem KNN von dem Zielwert abweicht, wird mit Hilfe einer Fehlerfunktion bestimmt. Es gibt verschiedene Arten von Fehlerfunktionen. Eine davon ist der mittlere quadratische Fehler (MQF):

  
    
      
        E
        =
        
          
            1
            2
          
        
        
          ∑
          
            i
            =
            1
          
          
            n
          
        
        (
        
          t
          
            i
          
        
        −
        
          o
          
            i
          
        
        
          )
          
            2
          
        
        .
      
    
    {\displaystyle E={\frac {1}{2}}\sum \limits _{i=1}^{n}(t_{i}-o_{i})^{2}.}
  

Dabei ist

  
    
      
        E
      
    
    {\displaystyle E}
  
 der Fehler,

  
    
      
        n
      
    
    {\displaystyle n}
  
 die Anzahl der Ausgabeneuronen,

  
    
      
        
          t
          
            i
          
        
      
    
    {\displaystyle t_{i}}
  
 die gewünschte Soll-Ausgabe oder Zielwert (target) und

  
    
      
        
          o
          
            i
          
        
      
    
    {\displaystyle o_{i}}
  
 die errechnete Ist-Ausgabe (output).
Der Faktor 
  
    
      
        
          
            
              1
              2
            
          
        
      
    
    {\displaystyle {\tfrac {1}{2}}}
  
 wird dabei lediglich zur Vereinfachung bei der Ableitung hinzugenommen.
Der MQF eignet sich, wenn die Rückgabe des Netzes ein einzelner Wert ist.

### Fehlerrückführung

Mit Hilfe des Fehlers lassen sich die Gewichte anpassen. Dies geschieht in zwei Schritten: Im ersten Schritt werden mit Hilfe der Fehlerrückführung die Gradienten bestimmt. Im zweiten Schritt werden die Gradienten mit einem Optimierungsverfahren verwendet, um die Gewichte zu aktualisieren. In diesem Abschnitt geht es um die Fehlerrückführung.
Die Idee hinter der Fehlerrückführung ist, die Gradienten schichtweise zu berechnen. Dies geschieht über die Kettenregel:

  
    
      
        
          
            
              
                ∂
                E
              
              
                ∂
                
                  w
                  
                    i
                    j
                  
                
              
            
          
        
        =
        
          
            
              ∂
              E
            
            
              ∂
              
                o
                
                  j
                
              
            
          
        
        
          
            
              ∂
              
                o
                
                  j
                
              
            
            
              ∂
              
                
                  
                    net
                  
                
                
                  j
                
              
            
          
        
        
          
            
              ∂
              
                
                  
                    net
                  
                
                
                  j
                
              
            
            
              ∂
              
                w
                
                  i
                  j
                
              
            
          
        
        .
      
    
    {\displaystyle {\dfrac {\partial E}{\partial w_{ij}}}={\frac {\partial E}{\partial o_{j}}}{\frac {\partial o_{j}}{\partial {\mbox{net}}_{j}}}{\frac {\partial {\mbox{net}}_{j}}{\partial w_{ij}}}.}

### Optimierung

Es ist wichtig, das Training mit zufälligen Anfangswerten zu beginnen. Bei überall gleichen Anfangswerten hätte beispielsweise jeder Knoten im KNN das gleiche Gewicht. Wenn dann Gewichte durch die Fehlerrückführung angepasst werden, würde der Fehler auf alle Knoten gleich verteilt und es würden auch alle Gewichte gleichmäßig verändert. Da das Problem in der Regel nicht symmetrisch ist, dürfen auch die Anfangswerte keine Symmetrien aufweisen, sonst kann der Lernalgorithmus das KNN nicht gut an die Trainingsdaten anpassen.
Mit der Fehlerrückführung wurden Fehler und Gewichte in einer Funktion abgebildet. Das Lernen korrespondiert nun zu einer Minimierung der Fehlerfunktion, indem die Gewichte angepasst werden. Das aus der Schule bekannte Optimalitätskriterium 1. Ordnung, das Nullsetzen der Ableitung, ist bei Neuronalen Netzen praktisch jedoch ungeeignet. Stattdessen wird mit Gradientenverfahren gearbeitet, um ein lokales Minimum der Fehlerfunktion zu finden. Der Gradient ist die Richtung des steilsten Anstieges einer Funktion, eine Bewegung entgegen den Gradienten ermöglicht also einen Abstieg auf dem Graphen der Fehlerfunktion. Eine Iteration des naiven Gradientverfahrens oder Gradientenabstieges ist also die Berechnung des Gradienten für die aktuelle Wahl der Gewichte, anschließend wird von den Gewichten der Gradient abgezogen und so neue Gewichte mit niedrigerem Fehler erhalten. Das Netz hat somit also „gelernt“.
Dieses Update bzw. dieser Abstiegsschritt wird durch folgende Zuweisung notiert:

  
    
      
        
          w
          
            i
          
        
        =
        
          w
          
            i
          
        
        −
        α
        
          
            
              ∂
              E
            
            
              ∂
              
                w
                
                  i
                
              
            
          
        
        .
      
    
    {\displaystyle w_{i}=w_{i}-\alpha {\frac {\partial E}{\partial w_{i}}}.}
  
Dabei beschreibt der Wert 
  
    
      
        α
      
    
    {\displaystyle \alpha }
  
 die Lernrate. Dieser gibt an, wie groß die Schritte sind, die das Verfahren in Richtung des Minimums nehmen soll. Zur Berechnung des Gradienten wird die Fehlerrückführung (engl. Backpropagation) verwendet. Das Verfahren wird solange wiederholt, bis ein Abbruchkriterium erfüllt ist, idealerweise durch Konvergenz zu einem lokalen Minimum.
Neben dem hier dargestellten naiven Gradientenverfahren werden in der Praxis meist besser entwickelte und leistungsfähigere Variationen des Gradientenabstieges verwendet, z. B. der stochastische Gradientenabstieg oder das ADAM-Verfahren.

## Anwendung

Seine besonderen Eigenschaften machen das KNN bei allen Anwendungen interessant, bei denen kein oder nur geringes explizites (systematisches) Wissen über das zu lösende Problem vorliegt. Dies sind z. B. die Texterkennung, Spracherkennung, Bilderkennung und Gesichtserkennung, bei denen einige Hunderttausend bis Millionen Bildpunkte in eine im Vergleich dazu geringe Anzahl von erlaubten Ergebnissen überführt werden müssen.
Auch in der Regelungstechnik kommen KNN zum Einsatz, um herkömmliche Regler zu ersetzen oder ihnen Sollwerte vorzugeben, die das Netz aus einer selbst entwickelten Prognose über den Prozessverlauf ermittelt hat. So können auch Fuzzy-Systeme durch eine bidirektionale Umwandlung in neuronale Netze lernfähig gestaltet werden.
Die Anwendungsmöglichkeiten sind aber nicht auf techniknahe Gebiete begrenzt: Bei der Vorhersage von Veränderungen in komplexen Systemen werden KNNs unterstützend hinzugezogen, z. B. zur Früherkennung sich abzeichnender Tornados oder aber auch zur Abschätzung der weiteren Entwicklung wirtschaftlicher Prozesse.
Zu den Anwendungsgebieten von KNNs gehören insbesondere:

Regelung und Analyse komplexer Prozesse
Frühwarnsysteme
Fehlererkennung
Optimierung
Zeitreihenanalyse (Wetter, Aktien usw.)
Sprachsynthese
Klangsynthese
Klassifikation
Bildverarbeitung und Mustererkennung
Schrifterkennung (OCR)
Spracherkennung
Data-Mining
Maschinenübersetzung
Gesichtserkennung
Gesichtsaustausch
Informatik: Bei Robotik, virtuellen Agenten und KI-Modulen in Spielen und Simulationen
Medizinische Diagnostik, Epidemiologie und Biometrie
Strukturgleichungsmodell zum Modellieren von sozialen oder betriebswirtschaftlichen Zusammenhängen
Trotz dieser sehr großen Spanne an Anwendungsgebieten gibt es Bereiche, die KNNs aufgrund ihrer Natur nicht abdecken können, beispielsweise:

Vorhersage von Zufalls- oder Pseudozufalls-Zahlen
Faktorisierung von großen Zahlen
Bestimmung, ob eine große Zahl prim ist
Entschlüsseln von verschlüsselten Texten

### Implementierungen

TensorFlow – Programmbibliothek
SNNS – Stuttgarter Neuronale-Netze-Simulator
EpsiloNN neuronale Beschreibungssprache der Universität Ulm
OpenNN

## Biologische Motivation

Während das Gehirn zur massiven Parallelverarbeitung in der Lage ist, arbeiten die meisten heutigen Computersysteme nur sequentiell (bzw. partiell parallel eines Rechners). Es gibt jedoch auch erste Prototypen neuronaler Rechnerarchitekturen, sozusagen den neuronalen Chip, für die das Forschungsgebiet der künstlichen neuronalen Netze die theoretischen Grundlagen bereitstellt. Dabei werden die physiologischen Vorgänge im Gehirn jedoch nicht nachgebildet, sondern nur die Architektur der massiv parallelen Analog-Addierer in Silizium nachgebaut, was gegenüber einer Software-Emulation eine bessere Leistung verspricht.

## Klassen und Typen von KNN

Grundsätzlich unterscheiden sich die Klassen der Netze vorwiegend durch die unterschiedlichen Netztopologien und Verbindungsarten, so zum Beispiel einschichtige, mehrschichtige, Feedforward- oder Feedback-Netze.

McCulloch-Pitts-Netze
Lernmatrix
Perzeptron
Adaline-Modell
Convolutional Neural Network (CNN)
Self-Organizing Maps (auch Kohonen-Netze) (SOM)
Growing Neural Gas (GNG)
Lernende Vektorquantisierung (LVQ)
Boltzmann-Maschine
Cascade-Correlation-Netze
Counterpropagation-Netze
Probabilistische neuronale Netze
Radiale Basisfunktions-Netze (RBF)
Adaptive Resonanztheorie (ART)
Neocognitron
Gepulste neuronale Netze (Spiking Neural Networks, SNN)
Pulscodierte neuronale Netze (PCNN)
Time Delay Neural Networks (TDNNs)
Rekurrente neuronale Netze (RNNs)
Bidirektionaler Assoziativspeicher (BAM)
Hopfield-Netze
Elman-Netze (auch Simple recurrent network, SRN)
Jordan-Netze
Oszillierendes neuronales Netz
Residuale neuronale Netze

## Lernverfahren

Lernverfahren dienen dazu, ein neuronales Netz so zu modifizieren, dass es für bestimmte Eingangsmuster zugehörige Ausgabemuster erzeugt. Dies geschieht grundsätzlich auf drei verschiedenen Wegen.

### Überwachtes Lernen (supervised learning)

Beim Überwachten Lernen wird dem KNN ein Eingangsmuster gegeben und die Ausgabe, die das neuronale Netz in seinem aktuellen Zustand produziert, mit dem Wert verglichen, den es eigentlich ausgeben soll. Durch Vergleich von Soll- und Istausgabe kann auf die vorzunehmenden Änderungen der Netzkonfiguration geschlossen werden. Bei einlagigen Perzeptrons kann die Delta-Regel (auch Perzeptron-Lernregel) angewendet werden. Mehrlagige Perzeptrons werden in der Regel mit Backpropagation trainiert, was eine Verallgemeinerung der Delta-Regel darstellt.

### Unüberwachtes Lernen (unsupervised learning)

Das Unüberwachte Lernen erfolgt ausschließlich durch Eingabe der zu lernenden Muster. Das neuronale Netz verändert sich entsprechend den Eingabemustern von selbst. Hierbei gibt es folgende Lernregeln:

Adaptive Resonanztheorie
Hebbsche Lernregel

### Bestärkendes Lernen (reinforcement learning)

Es ist nicht immer möglich, zu jedem Eingabedatensatz den passenden Ausgabedatensatz zum Trainieren zur Verfügung zu haben. Zum Beispiel kann man einem Agenten, der sich in einer fremden Umgebung zurechtfinden muss – etwa einem Roboter auf dem Mars – nicht zu jedem Zeitpunkt sagen, welche Aktion jeweils die beste ist. Aber man kann dem Agenten eine Aufgabe stellen, die dieser selbstständig lösen soll. Nach einem Testlauf, der aus mehreren Zeitschritten besteht, kann der Agent bewertet werden. Aufgrund dieser Bewertung kann eine Agentenfunktion gelernt werden.
Der Lernschritt kann durch eine Vielzahl von Techniken vollzogen werden. Unter anderem können hier auch künstliche neuronale Netze zum Einsatz kommen.

### Stochastisches Lernen

Simulierte Abkühlung (Simulated Annealing)

## Allgemeine Probleme

Die Hauptnachteile von KNN sind gegenwärtig:

Das Trainieren von KNN (im Terminus der Statistik: Das Schätzen der im Modell enthaltenen Parameter) führt in der Regel zu hochdimensionalen, nichtlinearen Optimierungsproblemen. Die prinzipielle Schwierigkeit bei der Lösung dieser Probleme besteht in der Praxis häufig darin, dass man nicht sicher sein kann, ob man das globale Optimum gefunden hat oder nur ein lokales. Obgleich in der Mathematik eine Fülle relativ schnell konvergierender lokaler Optimierungsverfahren entwickelt wurden (beispielsweise Quasi-Newton-Verfahren: BFGS, DFP usw.), finden auch diese selten optimale Lösungen. Eine zeitaufwändige Näherung an die globale Lösung erreicht man gegebenenfalls durch die vielfache Wiederholung der Optimierung mit immer neuen Startwerten.
Es müssen Trainings- und Testdaten gesammelt oder manuell erzeugt werden. Dieser Vorgang kann sehr schwierig sein, da man verhindern muss, dass das Netz Eigenschaften der Muster lernt, die zwar auf dem Trainingsset mit dem Ergebnis in irgendeiner Weise korreliert sind, die aber in anderen Situationen nicht zur Entscheidung herangezogen werden können oder sollen. Wenn beispielsweise die Helligkeit von Trainingsbildern bestimmte Muster aufweist, dann „achtet“ das Netz unter Umständen nicht mehr auf die gewünschten Eigenschaften, sondern klassifiziert die Daten nur noch aufgrund der Helligkeit. Im sozialen Bereich besteht z. B. die Gefahr, durch einseitig ausgewählte Testdaten bestehende Diskriminierungen (etwa aufgrund des Geschlechts oder der Herkunft) fortzuschreiben, ohne die eigentlich angezielten Kriterien (etwa Kreditwürdigkeit) ausreichend zu berücksichtigen.
Bei Anwendung einer heuristischen Vorgehensweise bei der Netzspezifikation neigen KNN dazu, die Trainingsdaten einfach auswendig zu lernen, infolge Übergeneralisierung bzw. Überanpassung (englisch overfitting). Wenn dies geschieht, können die Netze nicht mehr auf neue Daten verallgemeinern. Um eine Überanpassung zu vermeiden, muss die Netzarchitektur mit Bedacht gewählt werden. In ähnlicher Weise besteht diese Problematik auch bei vielen anderen statistischen Verfahren und wird als Verzerrung-Varianz-Dilemma bezeichnet. Verbesserte Verfahren setzen Boosting, Support-Vector-Maschinen oder Regularisierung ein, um diesem Problem zu begegnen.
Die Kodierung der Trainingsdaten muss problemangepasst und nach Möglichkeit redundanzfrei gewählt werden. In welcher Form die zu lernenden Daten dem Netz präsentiert werden, hat einen großen Einfluss auf die Lerngeschwindigkeit, sowie darauf, ob das Problem überhaupt von einem Netz gelernt werden kann. Gute Beispiele hierfür sind Sprachdaten, Musikdaten oder auch Texte. Das einfache Einspeisen von Zahlen, beispielsweise aus einer .wav-Datei für Sprache, führt selten zu einem erfolgreichen Ergebnis. Je präziser das Problem allein durch die Vorverarbeitung und Kodierung gestellt wird, desto erfolgreicher kann ein KNN dieses verarbeiten.
Die Vorbelegung der Gewichte spielt eine wichtige Rolle. Als Beispiel sei ein 3-schichtiges Feed-Forward-Netz mit einem Eingabeneuron (plus ein Bias-Neuron) und einem Ausgabeneuron und einer verdeckten Schicht mit N Neuronen (plus ein Bias-Neuron) angenommen. Die Aktivierungsfunktion des Eingabeneurons sei die Identität. Die Aktivierungsfunktion der verdeckten Schicht sei die Tanh-Funktion. Die Aktivierungsfunktion der Ausgabeschicht sei die logistische Sigmoide. Das Netz kann maximal eine Sinusfunktion mit N lokalen Extrema im Intervall von 0 bis 1 lernen. Wenn es diese Sinusfunktion gelernt hat, kann es mit dieser Gewichtsbelegung jede beliebige Funktion – die nicht mehr lokale Extrema als diese Sinusfunktion – mit möglicherweise exponentieller Beschleunigung – lernen (unabhängig vom Lernalgorithmus). Hier sei der einfachste Backpropagation ohne Momentum verwendet. Glücklicherweise kann man die Gewichte für solch eine Sinusfunktion leicht berechnen, ohne dass das Netz das erst lernen muss: Verdeckte Schicht : 
  
    
      
        i
        =
        0
        …
        N
        −
        1
      
    
    {\displaystyle i=0\ldots N-1}
  
, x = i % 2 == 0 ? 1 : -1 , 
  
    
      
        
          w
          
            0
            i
          
        
        =
        x
        ⋅
        π
        ⋅
        (
        N
        −
        0
        
          ,
        
        5
        )
        ,
        
          w
          
            l
            i
          
        
        =
        −
        x
        ⋅
        i
        ⋅
        π
      
    
    {\displaystyle w_{0i}=x\cdot \pi \cdot (N-0{,}5),w_{li}=-x\cdot i\cdot \pi }
  
; Ausgabeschicht : 
  
    
      
        
          w
          
            j
          
        
        =
        1
      
    
    {\displaystyle w_{j}=1}
  
.

## Filmische Dokumentationen

Künstliche neuronale Netze - Computer lernen sehen, einfache Erklärung, 2017
Künstliche neuronale Netze, komplexere Erklärung
Künstliche neuronale Netze - Programme lernen, einfache Erklärung, 2017
