---
title: Convolutional Neural Network
url: https://de.wikipedia.org/wiki/Convolutional_Neural_Network
updated: '2026-10-20T20:00:33Z'
language: de
revision: '271493609'
license: CC BY-SA 4.0
source: Wikipedia
---

Ein Convolutional Neural Network (CNN oder ConvNet), zu Deutsch etwa „faltendes neuronales Netzwerk“, ist ein künstliches neuronales Netz. Es handelt sich um ein von biologischen Prozessen inspiriertes Konzept im Bereich des maschinellen Lernens. Convolutional Neural Networks finden Anwendung in zahlreichen Technologien der künstlichen Intelligenz, vornehmlich bei der maschinellen Verarbeitung von Bild- oder Audiodaten.
Die CNN-Architektur wurde 1979 von Kunihiko Fukushima unter dem Namen Neocognitron eingeführt. Im Jahr 1987 trainierte Alex Waibel ein CNN namens TDNN durch Backpropagation und erzielte damit Bewegungsinvarianz. Auch Yann LeCun publizierte ab dem Ende der 1980er Jahre wichtige Beiträge zu CNNs.

## Aufbau

Grundsätzlich besteht die Struktur eines klassischen Convolutional Neural Networks aus einem oder mehreren Convolutional Layer, gefolgt von einem Pooling Layer.
Diese Einheit kann sich prinzipiell beliebig oft wiederholen, bei ausreichend Wiederholungen spricht man dann von Deep Convolutional Neural Networks, die in den Bereich Deep Learning fallen.
Hierbei ist auf die Ähnlichkeit zum Optimalfilter hinzuweisen.
Architektonisch können im Vergleich zum mehrlagigen Perzeptron (Multi-Layer-Perzeptron) drei wesentliche Unterschiede festgehalten werden (Details hierzu siehe Convolutional Layer):

2D- oder 3D-Anordnung der Neuronen
Geteilte Gewichte
Lokale Konnektivität

### Convolutional Layer

In der Regel liegt die Eingabe als zwei- oder dreidimensionale Matrix (z. B. die Pixel eines Graustufen- oder Farbbildes) vor. Dementsprechend sind die Neuronen im Convolutional Layer angeordnet.
Die Aktivität jedes Neurons wird über eine diskrete Faltung (daher der Zusatz convolutional) berechnet. Dabei wird schrittweise eine vergleichsweise kleine Faltungsmatrix (Filterkernel) über die Eingabe bewegt. Die Eingabe eines Neurons im Convolutional Layer berechnet sich als inneres Produkt des Filterkernels mit dem aktuell unterliegenden Bildausschnitt. Dementsprechend reagieren benachbarte Neuronen im Convolutional Layer auf sich überlappende Bereiche (ähnliche Frequenzen in Audiosignalen oder lokale Umgebungen in Bildern).

Hervorzuheben ist, dass ein Neuron in diesem Layer nur auf Reize in einer lokalen Umgebung des vorherigen Layers reagiert. Dies folgt dem biologischen Vorbild des rezeptiven Feldes. Zudem sind die Gewichte für alle Neuronen eines Convolutional Layers identisch (geteilte Gewichte, englisch: shared weights). Dies führt dazu, dass beispielsweise jedes Neuron im ersten Convolutional Layer codiert, zu welcher Intensität eine Kante in einem bestimmten lokalen Bereich der Eingabe vorliegt. Die Kantenerkennung als erster Schritt der Bilderkennung besitzt hohe biologische Plausibilität. Aus den shared weights folgt unmittelbar, dass Translationsinvarianz eine inhärente Eigenschaft von CNNs ist.
Der mittels diskreter Faltung ermittelte Input eines jeden Neurons wird nun von einer Aktivierungsfunktion, bei CNNs üblicherweise Rectified Linear Unit, kurz ReLU (
$f(x)=\max(0,x)$

), in den Output verwandelt, der die relative Feuerfrequenz eines echten Neurons modellieren soll. Da Backpropagation die Berechnung der Gradienten verlangt, wird in der Praxis eine differenzierbare Approximation von ReLU benutzt: 
$f(x)=\ln(1+e^{x})$

Analog zum visuellen Cortex steigt in tiefer gelegenen Convolutional Layers sowohl die Größe der rezeptiven Felder (siehe Sektion Pooling Layer) als auch die Komplexität der erkannten Features (beispielsweise Teile eines Gesichts).
Eine Faltung ist die einfache Anwendung eines Filters auf eine Eingabe, die zu einer Aktivierung führt. Die wiederholte Anwendung desselben Filters auf eine Eingabe führt zu einer Karte von Aktivierungen, die als Feature Map bezeichnet wird und die Positionen und die Stärke eines erkannten Features in einer Eingabe, beispielsweise einem Bild, angibt. Convolutional Layer können automatisch eine große Anzahl von Filtern parallel lernen, die für einen Trainingsdatensatz spezifisch sind. Das Ergebnis sind hochspezifische Merkmale, die überall auf Eingabebildern erkannt werden können. Convolutional Layer wenden einen Filter auf eine Eingabe an, um eine Feature Map zu erstellen, die das Vorhandensein erkannter Features in der Eingabe zusammenfasst.
Eine Faltung ist eine lineare Operation, die die Multiplikation einer Reihe von Gewichten mit der Eingabe beinhaltet, ähnlich wie bei einem herkömmlichen neuronalen Netz. Der Filter ist kleiner als die Eingabedaten und die Art der Multiplikation, die zwischen einem filtergroßen Patch der Eingabe und dem Filter angewendet wird, ist ein Skalarprodukt. Die Verwendung eines Filters, der kleiner als die Eingabe ist, ist beabsichtigt, weil dadurch derselbe Filter an verschiedenen Stellen der Eingabe mehrmals mit dem Eingabearray multipliziert werden kann. Konkret wird der Filter systematisch auf jeden überlappenden Teil oder filtergroßen Patch der Eingabedaten angewendet, von links nach rechts, von oben nach unten. Diese systematische Anwendung desselben Filters auf ein Bild ist eine wirkungsvolle Idee. Wenn der Filter darauf ausgelegt ist, einen bestimmten Merkmalstyp in der Eingabe zu erkennen, kann der Filter dieses Merkmal an einer beliebigen Stelle im Bild erkennen. Diese Fähigkeit wird allgemein als Übersetzungsinvarianz bezeichnet, zum Beispiel das allgemeine Interesse daran, ob das Merkmal vorhanden ist, und nicht, wo es vorhanden war.
Die Convolutional Layer ist der Kernbaustein des Convolutional Neural Network. Es trägt den Hauptanteil der Rechenlast des Netzwerks. Diese Schicht führt ein Skalarprodukt zwischen zwei Matrizen aus, wobei eine Matrix der Satz von gelernten Parametern ist, die auch als Kernel bezeichnet werden, und die andere Matrix der eingeschränkte Teil des Empfangsfeldes. Der Kernel ist räumlich kleiner als ein Bild, ist aber ausführlicher. Dies bedeutet, dass, wenn das Bild aus drei Kanälen besteht, die Höhe und die Breite des Kernels räumlich klein sind, die Tiefe bis zu allen drei Kanälen erstreckt. Dies erzeugt eine zweidimensionale Darstellung des als Aktivierungskarte bekannten Bildes, die die Antwort des Kernels an jeder räumlichen Position des Bildes ergibt. Die Gleitgröße des Kernels wird als Schritt bezeichnet.
Wenn man eine Eingabe der Größe 
$W\times W\times D$

 und 
$D_{out}$

 Kerne mit einer räumlichen Größe von 
$F$

 mit Schrittweite 
$S$

 und dem Betrag der Füllung 
$P$

 hat, kann die Größe des Ausgabevolumens durch die folgende Formel bestimmt werden:

$W_{out}={\frac {W-F+2\cdot P}{S}}+1$

### Pooling Layer

Im folgenden Schritt, dem Pooling, werden überflüssige Informationen verworfen. Zur Objekterkennung in Bildern etwa ist die exakte Position einer Kante im Bild von vernachlässigbarem Interesse – die ungefähre Lokalisierung eines Features ist hinreichend.
Es gibt verschiedene Arten des Poolings. Mit Abstand am stärksten verbreitet ist das Max-Pooling, wobei aus jedem 2×2-Quadrat aus Neuronen des Convolutional Layers nur die Aktivität des aktivsten (daher „Max“) Neurons für die weiteren Berechnungsschritte beibehalten wird; die Aktivität der übrigen Neuronen wird verworfen (siehe Bild).
Trotz der Datenreduktion (im Beispiel 75 %) verringert sich in der Regel die Performance des Netzwerks nicht durch das Pooling. Im Gegenteil, es bietet einige signifikante Vorteile:

Verringerter Platzbedarf und erhöhte Berechnungsgeschwindigkeit
Daraus resultierende Möglichkeit zur Erzeugung tieferer Netzwerke, die komplexere Aufgaben lösen können
Automatisches Wachstum der Größe der rezeptiven Felder in tieferen Convolutional Layers (ohne dass dafür explizit die Größe der Faltungsmatrizen erhöht werden müsste)
Präventionsmaßnahme gegen Overfitting
Alternativen wie das Mean-Pooling haben sich in der Praxis als weniger effizient erwiesen.
Das biologische Pendant zum Pooling ist die laterale Hemmung im visuellen Cortex.
Die Pooling Layer ersetzt die Ausgabe des Netzwerks an bestimmten Stellen, indem er eine zusammenfassende Statistik der nahe gelegenen Ausgaben abgeleitet hat. Dies hilft bei der Verringerung der räumlichen Größe der Darstellung, die die erforderliche Menge an Rechen und Gewichten verringert. Die Pooling-Operation wird auf jedem Stück der Darstellung einzeln ausgeführt. Das beliebteste Verfahren ist Max Pooling, die die maximale Ausgabe aus der Nachbarschaft angibt. Wenn man eine Aktivierungskarte der Größe 
$W\times W\times D$

, einen Pooling Kernel der räumlichen Größe 
$F$

 mit Schrittweite 
$S$

 hat, kann die Größe des Ausgabevolumens durch die folgende Formel bestimmt werden:

$W_{out}={\frac {W-F}{S}}+1$

Dies ergibt ein Ausgabevolumen der Größe 
$W_{out}\times W_{out}\times D$

.

#### Max Pooling

Max Pooling ist eine Faltungstechnik, die den Maximalwert aus dem Patch der Eingabedaten auswählt und diese Werte in einer Feature Map zusammenfasst: Diese Methode behält die wichtigsten Merkmale der Eingabe bei, indem sie ihre Abmessungen reduziert. Die mathematische Formel für Max Pooling lautet:

$\mathrm {MaxPooling} (x)_{i,j,k}=\max _{m,n}{X_{i\cdot x_{s}+m,j\cdot y_{s}+n,k}}$

Dabei sind 
$X$

 die Eingabe, 
$(i,j)$

 die Indexe der Ausgabe, 
$k$

 der Kanalindex, 
$s_{x}$

 und 
$s_{y}$

 die Schrittwerte in horizontaler bzw. vertikaler Richtung und das Pooling-Fenster wird durch die Filtergrößen 
$f_{x}$

 und 
$f_{x}$

 definiert, zentriert am Ausgabeindex 
$(i,j)$

.

#### Average Pooling

Durch das Average Pooling wird der Durchschnittswert aus einem Bereich von Eingabedaten berechnet und diese Werte in einer Feature Map zusammengefasst. Diese Methode ist in Fällen vorzuziehen, in denen eine Glättung der Eingabedaten erforderlich ist, da sie dabei hilft, das Vorhandensein von Ausreißern zu identifizieren. Die mathematische Formel für Average Pooling lautet:

$\mathrm {AvgPooling} (x)_{i,j,k}={\frac {1}{f_{x}\cdot f_{y}}}\cdot \sum _{m,n}X_{i\cdot x_{s}+m,j\cdot y_{s}+n,k}$

#### Global Pooling

Global Pooling fasst die Werte aller Neuronen für jeden Patch der Eingabedaten in einer Feature Map zusammen, unabhängig von ihrer räumlichen Position. Diese Technik wird auch verwendet, um die Dimensionalität der Eingabe zu reduzieren und kann entweder mithilfe der maximalen oder durchschnittlichen Pooling-Operation durchgeführt werden. Die mathematische Formel für Global Pooling lautet:

$\mathrm {GlobalPooling} (x)_{k}=f_{x}(X:,:,k)$

#### Stochastic Pooling

Stochastic Pooling ist eine nicht-deterministische Pooling-Operation, die zufällige Werte mit Max Pooling kombiniert. Diese Technik trägt dazu bei, die Robustheit des Modells gegenüber kleinen Abweichungen in den Eingabedaten zu verbessern. Die mathematische Formel für Stochastic Pooling lautet:

$\operatorname {StochasticPooling} (x)_{i,j,k}={\begin{cases}X_{i,j,k}&{\text{mit Wahrscheinlichkeit }}p_{i,k}\\0&{\text{mit Wahrscheinlichkeit }}1-p_{i,k}\end{cases}}$

Dabei sind 
$X$

 die Eingabe, 
$i,j$

 die Indizes des Ausgabetensors, 
$k$

 der Kanalindex und 
$p_{i,j}$

 die Wahrscheinlichkeit, den Wert an Position 
$(i,j)$

 in der Feature Map der Eingabe beizubehalten. Die Wahrscheinlichkeiten werden für jedes Pooling-Fenster zufällig generiert und sind normalerweise proportional zu den Werten im Fenster.

### Fully-connected Layer

Nach einigen sich wiederholenden Einheiten bestehend aus Convolutional und Pooling Layer kann das Netzwerk mit einem (oder mehreren) Fully-connected Layer entsprechend der Architektur des mehrlagigen Perzeptrons abschließen. Dies wird vor allem bei der Klassifizierung angewendet. Die Anzahl der Neuronen im letzten Layer korrespondiert dann üblicherweise zu der Anzahl an (Objekt-)Klassen, die das Netz unterscheiden soll. Dieses, sehr redundante, sogenannte One-Hot-encoding hat den Vorteil, dass keine impliziten Annahmen über Ähnlichkeiten von Klassen gemacht werden.
Die Ausgabe der letzten Schicht des CNNs wird in der Regel durch eine Softmax-Funktion, einer translations- aber nicht skaleninvarianten Normalisierung über alle Neuronen im letzten Layer, in eine Wahrscheinlichkeitsverteilung überführt.

### Convolution Operator

Der Convolution Operator ist definiert als Faltung 
$x*w$

 auf den reellen Funktionen 
$x$

 und 
$w$

:

$s(t)=(w*x)(t)=\int x(a)w(t-a)\mathrm {d} a$

Die Zeit wird meistens diskret definiert:

$s(t)=(w*x)(t)=\sum _{a=-\infty }^{\infty }x(a)w(t-a)$

In Anwendungen mit zweidimensionalen Arrays als Input und Kern gilt

$S(i,j)=(I*K)(i,j)=\sum _{m}\sum _{n}I(m,n)\cdot K(i-m,j-n)$

Der Convolution Operator ist kommutativ, d. h., es gilt

$S(i,j)=(K*I)(i,j)=\sum _{m}\sum _{n}I(i-m,j-n)\cdot K(m,n)$

Außerdem gilt die Cross-Relation:

$S(i,j)=(K*I)(i,j)=\sum _{m}\sum _{n}I(i+m,j+n)\cdot K(m,n)$

## Training

CNNs werden in aller Regel überwacht trainiert. Während des Trainings wird dabei für jeden gezeigten Input der passende One-Hot-Vektor bereitgestellt. Via Backpropagation wird der Gradient eines jeden Neurons berechnet und die Gewichte werden in Richtung des steilsten Abfalls der Fehleroberfläche angepasst.
Interessanterweise haben drei vereinfachende Annahmen, die den Berechnungsaufwand des Netzes maßgeblich verringern und damit tiefere Netzwerke zulassen, wesentlich zum Erfolg von CNNs beigetragen.

Pooling – Hierbei wird der Großteil der Aktivität eines Layers schlicht verworfen.
ReLU – Die gängige Aktivierungsfunktion, die jeglichen negativen Input auf 0 projiziert.
Dropout – Eine Regularisierungsmethode beim Training, die Overfitting verhindert. Dabei werden pro Trainingsschritt zufällig ausgewählte Neuronen aus dem Netzwerk entfernt.

## Expressivität und Notwendigkeit

Da CNNs eine Sonderform von mehrlagigen Perzeptrons darstellen, sind sie prinzipiell identisch in ihrer Ausdrucksstärke.
Der Erfolg von CNNs lässt sich mit ihrer kompakten Repräsentation der zu lernenden Gewichte („shared weights“) erklären. Grundlage ist die Annahme, dass ein potentiell interessantes Feature (In Objekterkennung etwa Kanten) an jeder Stelle des Inputsignals (des Bildes) interessant ist. Während ein klassisches zweilagiges Perzeptron mit jeweils 1000 Neuronen pro Ebene für die Verarbeitung von einem Bild im Format 32 × 32 insgesamt mehr als 2 Millionen Gewichte benötigt, verlangt ein CNN mit zwei sich wiederholenden Einheiten, bestehend aus insgesamt 13.000 Neuronen, nur 160.000 (geteilte) zu lernende Gewichte, wovon der Großteil im hinteren Bereich (fully-connected Layer) liegt.
Neben dem wesentlich verringerten Arbeitsspeicherbedarf haben sich geteilte Gewichte als robust gegenüber Translations-, Rotations-, Skalen- und Luminanzvarianz erwiesen.
Um mithilfe eines mehrlagigen Perzeptrons eine ähnliche Performance in der Bilderkennung zu erreichen, müsste dieses Netzwerk jedes Feature für jeden Bereich des Inputsignals unabhängig erlernen. Dies funktioniert zwar ausreichend für stark verkleinerte Bilder (etwa 32 × 32), aufgrund des Fluchs der Dimensionalität scheitern MLPs jedoch an höher auflösenden Bildern.

## Biologische Plausibilität

CNNs können als ein vom visuellen Cortex inspiriertes Konzept verstanden werden, sind jedoch weit davon entfernt, neuronale Verarbeitung plausibel zu modellieren.
Einerseits gilt das Herzstück von CNNs, der Lernmechanismus Backpropagation, als biologisch unplausibel, da es bis heute trotz intensiver Bemühungen nicht gelungen ist, neuronale Korrelate von backpropagation-ähnlichen Fehlersignalen zu finden.
Neben dem stärksten Gegenargument zur biologischen Plausibilität – der Frage, wie der Kortex Zugriff auf das Zielsignal (Label) bekommt – listen Bengio et al. weitere Gründe, darunter die binäre, zeitkontinuierliche Kommunikation biologischer Neurone sowie die Berechnung nicht-linearer Ableitungen der Vorwärtsneuronen.
Andererseits konnte durch Untersuchungen mit fMRT gezeigt werden, dass Aktivierungsmuster einzelner Schichten eines CNNs mit den Neuronenaktivitäten in bestimmten Arealen des visuellen Cortex korrelieren, wenn sowohl das CNN als auch die menschlichen Testprobanden mit ähnlichen Aufgaben aus der Bildverarbeitung konfrontiert werden. Neuronen im primären visuellen Cortex, die sogenannten „simple cells“, reagieren auf Aktivität in einem kleinen Bereich der Retina. Dieses Verhalten wird in CNNs durch die diskrete Faltung in den convolutional Layers modelliert. Funktional sind diese biologischen Neuronen für die Erkennung von Kanten in bestimmten Orientierungen zuständig. Diese Eigenschaft der simple cells kann wiederum mithilfe von Gabor-Filtern präzise modelliert werden. Trainiert man ein CNN zur Objekterkennung, konvergieren die Gewichte im ersten Convolutional Layer ohne jedes „Wissen“ über die Existenz von simple cells gegen Filtermatrizen, die Gabor-Filtern erstaunlich nahe kommen, was als Argument für die biologische Plausibilität von CNNs verstanden werden kann. Angesichts einer umfassenden statistischen Informationsanalyse von Bildern mit dem Ergebnis, dass Ecken und Kanten in verschiedenen Orientierungen die am stärksten voneinander unabhängigen Komponenten in Bildern – und somit die fundamentalsten Grundbausteine zur Bildanalyse – sind, ist dies jedoch zu erwarten.
Somit treten die Analogien zwischen Neuronen in CNNs und biologischen Neuronen primär behavioristisch zutage, also im Vergleich zweier funktionsfähiger Systeme, wohingegen die Entwicklung eines „unwissenden“ Neurons zu einem (beispielsweise) gesichtserkennenden Neuron in beiden Systemen diametralen Prinzipien folgt.

## Probleme

Neuronale Feedforward-Netze können jede stetige Funktion der Form 
$f\colon X\in \mathbb {R} ^{n}\mapsto Y\in \mathbb {R} ^{m}$

 annähern, dies wird durch das universelle Approximationstheorem garantiert. Es gibt jedoch keine Garantie dafür, dass das Training dies auch ermöglicht. Wird während dem Training keine Regularisierung verwendet, wird ein neuronales Netz überangepasst auf das Rauschen in den Trainingsdaten. Durch die Verringerung der Modellkapazität durch Wiederverwendung der Gewichte mithilfe einer Faltung (als eine bestimmte Art der Regularisierung) kann die Tendenz zur Überanpassung verringert werden.
Formal bedeutet dies, dass die Merkmale 
$X\mapsto X'$

 transformiert werden, so dass, wenn 
$H(X)$

 die Entropie von 
$X$

 ist, dann gilt 
$H(X)\leq H(X')$

. Dadurch kann das neuronale Netz eine neue Zielfunktion 
$g\colon f(X)\mapsto g(X')$

 lernen, die weniger anfällig für Überanpassung ist. Dies wird dadurch ermöglicht, dass eine wichtige Voraussetzung, die lineare Unabhängigkeit der Merkmale, für einige Datenklassen systematisch verletzt wird.

## Anwendung

Seit dem Einsatz von Grafikprozessor-Programmierung können CNNs erstmals effizient trainiert werden. Sie gelten als State-of-the-Art-Methode für zahlreiche Anwendungen im Bereich der Klassifizierung.

### Bilderkennung

Im Jahr 2012 verbesserte das CNN AlexNet die Fehlerquote beim jährlichen Wettbewerb der Benchmark-Datenbank ImageNet (ILSVRC) von dem vormaligen Rekord von 25,8 % auf 16,4 %. Seitdem nutzen alle vorne platzierten Algorithmen CNN-Strukturen. 
Im Jahr 2016 wurde schon eine Fehlerquote < 3 % erreicht. Auf der am häufigsten genutzten Bilddatenbanken MNIST wurde im selben Jahr eine Fehlerquote von 0,23 % erreicht, was der geringsten Fehlerquote aller jemals getesteten Algorithmen entsprach.
Auch im Bereich der Gesichtserkennung konnten bahnbrechende Resultate erzielt werden.

### Segmentierung

Fully convolutional networks (FCNs) sind eine spezielle Variante von CNNs, die ausschließlich Faltungsoperationen verwendet. Mit einem solchen Aufbau ist es möglich, für Input-Daten jeder Größe einen Output der entsprechenden Größe zu erzeugen. Sie sind besonders geeignet, um Bilddaten zu segmentieren. Ein prominenter und vielfach verwendeter Vertreter ist das entsprechend seiner gewöhnlichen Darstellungsform so bezeichnete U-Net.

### Spracherkennung

CNNs werden erfolgreich zur Spracherkennung eingesetzt und haben hervorragende Resultate in folgenden Bereichen erzielt:

semantisches Parsen
Suchanfragenrückerkennung
Satzmodellierung
Satzklassifizierung
Part-of-speech-Tagging
Maschinelle Übersetzung (z. B. verwendet im Online-Dienst DeepL)

### Reinforcement Learning

Angewendet werden können CNNs auch im Bereich Reinforcement Learning, bei dem ein CNN mit Q-Learning kombiniert wird. Das Netzwerk wird darauf trainiert zu schätzen, welche Aktionen bei einem gegebenen Zustand zu welchem zukünftigen Gewinn führen. Durch die Verwendung eines CNNs können so auch komplexe, höher-dimensionale Zustandsräume betrachtet werden, wie etwa die Bildschirmausgabe eines Videospiels.

### Landwirtschaft

CNNs werden heutzutage auch eingesetzt, um die Auswirkungen von Düngung vorherzusagen und Düngungsempfehlungen abzugeben.
