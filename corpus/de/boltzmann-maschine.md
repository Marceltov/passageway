---
title: Boltzmann-Maschine
url: https://de.wikipedia.org/wiki/Boltzmann-Maschine
updated: '2026-06-21T16:16:42Z'
language: de
revision: '268116312'
license: CC BY-SA 4.0
source: Wikipedia
---

Eine Boltzmann-Maschine ist ein neuronales Netz, das nach dem österreichischen Wissenschaftler Ludwig Boltzmann benannt wurde.
Boltzmann-Maschinen sind eine spezielle Art energiebasiertes Modell.
Entwickelt wurde sie von Geoffrey Hinton und Terrence J. Sejnowski im Jahre 1985. Die Boltzmann-Maschine wird auch stochastisches Hopfield-Netz mit versteckten Einheiten genannt.
Beschränkt man die Verbindungen zwischen den Neuronen, lässt sich der Lernvorgang stark vereinfachen – diese Boltzmann-Maschinen werden Beschränkte Boltzmann-Maschinen („restricted Boltzmann machines“) genannt.
Der Nobelpreis für Physik im Jahre 2024 ging an John Hopfield und Hinton für ihren fundamentalen Beitrag zum Maschinellen Lernen, insbesondere der Boltzmann-Maschine.

## Funktionsweise

Die Funktionsweise der Boltzmann-Maschine basiert auf der Boltzmann-Verteilung, die besagt, dass der aktuelle Zustand eines physikalischen Systems von der Energie und der Temperatur des Systems abhängt. Um Boltzmann-Maschinen als neuronale Netze zu implementieren, verwendet man daher die Energiemodelle. Der Energie entspricht die Abweichung von der tatsächlichen Antwort. Je höher die Energie, desto größer die Abweichung. Es ist daher wichtig, das Modell zu trainieren, bis es einen Niedrigenergiepunkt erreicht. Ein solches theoretisches Modell leidet unter dem Problem lokaler Minima und liefert weniger genaue Ergebnisse. Dieses Problem wurde gelöst, indem dem Modell erlaubt wurde, periodische Sprünge zu einem höheren Energiezustand zu machen und dann zurück zu den Minima zu konvergieren, was schließlich zu den globalen Minima führt.
Wenn Boltzmann-Maschinen beim Lernen eingesetzt werden, versuchen sie, wichtige Merkmale aus der Eingabe abzuleiten, diese Eingabe zu rekonstruieren und sie durch parallele Aktualisierung von Gewichten als Ausgabe wiederzugeben.
Boltzmann-Maschinen eignen sich gut, um ein Problem der Erfüllung von Einschränkungen zu lösen, selbst wenn es schwache Einschränkungen hat. Ein Problem mit schwachen Einschränkungen versucht, eine Lösung zu erhalten, die nahe genug an einer Lösung sein kann, die alle Einschränkungen vollständig erfüllt, d. h. die Lösung muss nicht alle Einschränkungen vollständig erfüllen.
Boltzmann-Maschinen haben keine klare Abgrenzung zwischen Eingabeschicht und Ausgabeschicht. Die Knoten in Boltzmann-Maschinen werden einfach als sichtbare und unsichtbare Knoten kategorisiert. Die sichtbaren Knoten nehmen die Eingabe auf. Dieselben Knoten, die die Eingabe aufnehmen, geben die rekonstruierte Eingabe als Ausgabe zurück. Dies wird durch bidirektionale Gewichtungen erreicht, die sich rückwärts ausbreiten und die Ausgabe auf den sichtbaren Knoten rendern. Ein wesentlicher Vorteil der Architektur besteht darin, dass jeder Knoten mit allen anderen Knoten verbunden ist. Alle Verbindungen sind bidirektional und die Gewichtungen sind symmetrisch.

## Formale Definition

Eine Boltzmann-Maschine ist ein Netzwerk aus symmetrisch gekoppelten stochastischen binären Einheiten. Sie umfasst eine Menge sichtbarer Knoten 
$v\in \{0,1\}^{D}$

 und eine Menge unsichtbarer Knoten 
$h\in \{0,1\}^{P}$

. Die Energie des Zustands 
$\{v,h\}$

 ist definiert als

$E(v,h;\theta )=-{\frac {1}{2}}\cdot v^{T}\cdot L\cdot v-{\frac {1}{2}}\cdot h^{T}\cdot J\cdot h+v^{T}\cdot W\cdot h$

wobei 
$\theta =\{W,L,J\}$

 die Modellparameter sind. Die Matrizen 
$W$

, 
$L$

, 
$J$

 stehen für symmetrische Interaktionsterme zwischen sichtbaren und unsichtbaren Knoten, zwischen sichtbaren Knoten untereinander sowie zwischen unsichtbaren Knoten untereinander. Die Diagonalelemente von 
$L$

 und 
$J$

 werden auf 0 gesetzt. Die Wahrscheinlichkeit, die das Modell einem sichtbaren Vektor 
$v$

 zuweist, beträgt

$p(v;\theta )=-{\frac {p^{*}(v;\theta )}{Z(\theta )}}={\frac {1}{Z(\theta )}}\cdot \sum _{h}\exp(-E(v,h,\theta ))$
$Z(\theta )=\sum _{v}\sum _{h}\exp(-E(v,h,\theta ))$

wobei 
$p^{*}$

 die unnormierte Wahrscheinlichkeit und 
$Z(\theta )$

 die Partitionsfunktion bezeichnet. Die bedingten Verteilungsfunktionen über die unsichtbaren und sichtbaren Knoten sind gegeben durch

$p(h_{j}=1|v,h_{-j})=\sigma \left(\sum _{i=1}^{D}W_{i,j}\cdot v_{i}+\sum _{m=1\setminus j}^{P}J_{j,m}\cdot h_{j}\right)$
$p(v_{i}=1|h,v_{-i})=\sigma \left(\sum _{j=1}^{P}W_{i,j}\cdot h_{j}+\sum _{k=1\setminus i}^{D}L_{i,k}\cdot v_{i}\right)$

wobei 
$\sigma (x)={\frac {1}{1+\exp(-x)}}$

 die logistische Funktion ist.

## Aufbau

Eine Boltzmann-Maschine hat das Lernziel eine parametrisierte Wahrscheinlichkeitsverteilung 
$P_{s_{v}}(\{w_{ij}\})$

 über den sichtbaren Zuständen 
$s_{v}$

 durch Lernen von Parametern 
$w_{ij}$

 zu approximieren. Die parametrisierte Wahrscheinlichkeitsverteilung ist die Boltzmannverteilung (siehe unten). Die Parameter 
$w_{ij}$

 werden durch Minimierung der Kullback-Leibler-Divergenz zwischen der vom Modell vorhergesagten Wahrscheinlichkeitsverteilung 
$P_{s_{v}}(\{w_{ii}\})$

 und der in den Trainingsdaten gefundenen Verteilung 
$P_{s_{v}}^{+}$

 gefunden:

$G=\sum _{v}{P_{s_{v}}^{+}\ln \left({\frac {P_{s_{v}}^{+}}{P_{s_{v}}}}\right)}$

.
Die Struktur der Boltzmann-Maschine ist (wie ein Hopfield-Netz) ein Netz von Neuronen (Zuständen), in dem ein Energieniveau definiert ist. Wie bei Hopfield-Netzen nehmen die Neuronen nur binäre Werte (0 oder 1) an, verhalten sich im Gegensatz jedoch stochastisch. Das Energieniveau 
$E$

 einer Boltzmann-Maschine wird benötigt, um die Wahrscheinlichkeitsverteilung 
$P_{s_{v}}$

 der Zustände zu parametrisieren. Die Energie ist so definiert wie bei einem Hopfield-Netz oder einem Ising-Modell:

$E=-{\frac {1}{2}}\sum _{i}\sum _{j}{s_{i}}{w_{ij}{s_{j}}}+\sum _{i}{\theta _{i}s_{i}}$

wobei gilt:

$w_{ij}$

 ist das Gewicht der Verbindung zwischen Neuron 
$i$

 und 
$j$

.

$s_{i}$

 ist der Zustand 
$s_{i}\in \{0,1\}$

 des Neurons 
$i$

.

$\theta _{i}$

 ist der Schwellwert eines Neurons 
$i$

. (
$-\theta _{i}$

 ist der Wert ab dem ein Neuron aktiviert wird.)
Die Verbindungen einer Boltzmann-Maschine haben zwei Beschränkungen:

$w_{ii}=0\qquad \forall i$

. (Kein Neuron hat eine Verbindung mit sich selbst.)

$w_{ij}=w_{ji}\qquad \forall i,j$

. (Alle Verbindungen sind symmetrisch.)
Die Gewichtungen lassen sich in Form einer symmetrischen Matrix 
$W$

 darstellen, deren Hauptdiagonale aus Nullen besteht.
Die Veränderung des Energieniveaus, die sich ergibt, wenn ein einzelnes Neuron 
$i$

 vom Zustand 
$s_{i}=1$

 zum Zustand 
$s_{i}=0$

 wechselt, beträgt

$\Delta E_{i}=E_{s_{i}=1}-E_{s_{i}=0}=\sum _{j\neq i}(w_{ij}{s_{j}}-\theta _{i})$

Mit den Größen der Boltzmann-Verteilung kann dies wie folgt geschrieben werden:

$\Delta E_{i}=-k_{B}T\ln(P_{s_{i}=1})-(-k_{B}T\ln(P_{s_{i}=0}))$

Daraus folgt

${\frac {\Delta E_{i}}{k_{B}T}}=\ln(P_{s_{i}=1})-\ln(P_{s_{i}=0})=\ln(P_{s_{i}=1})-\ln(1-P_{s_{i}=1})$

Aufgelöst nach der Wahrscheinlichkeit, dass das Neuron 
$i$

 den Zustand 
$s_{i}=1$

 hat, folgt daraus

$P_{s_{i}=1}={\frac {1}{1+e^{-{\frac {\Delta E_{i}}{k_{B}T}}}}}$

Das bedeutet, dass die Wahrscheinlichkeit, dass ein Neuron den Wert 1 annimmt, eine logistische Funktion der skalierten Veränderung des Energieniveaus zwischen seinem aktiven und inaktiven Zustand ist.
Genau wie beim Hopfield-Netz tendiert die Boltzmann-Maschine dazu, den Wert der so definierten Energie bei aufeinanderfolgenden Aktualisierungen zu verringern, letztendlich also zu minimieren, bis ein stabiler Zustand erreicht ist.

## Beschränkte Boltzmann-Maschinen

Eine sog. Restricted Boltzmann Machine (RBM) besteht aus sichtbaren Einheiten (engl. visible units) und versteckten Einheiten (hidden units). An die sichtbaren Einheiten wird der Feature-Vektor angelegt.
Das „restricted“ (englisch für „beschränkt“) bezeichnet die Tatsache, dass weder die sichtbaren Einheiten noch die versteckten Einheiten innerhalb dieser Gruppen untereinander verbunden sind. Allerdings sind die sichtbaren Einheiten mit den versteckten Einheiten vollständig verbunden. Sie bilden also einen bipartiten ungerichteten Graphen. Dies ist im Folgenden dargestellt:

Die zu lernenden Parameter sind die Gewichte der Kanten zwischen sichtbaren und versteckten Einheiten sowie die Bias-Vektoren 
$b_{h},b_{v}$

 der versteckten und der sichtbaren Einheiten. Diese werden über den Contrastive-Divergence-Algorithmus gelernt.
Die paarweisen Wechselwirkungen sind auf Verbindungen zwischen der Menge der sichtbaren Einheiten und der Menge der versteckten Einheiten beschränkt. Diese Modelle wurden im Kontext der Harmonie-Theorie und unüberwacht lernender zweischichtiger Netzwerke eingeführt. RBMs spielten eine Schlüsselrolle bei der Entwicklung gieriger, schichtweiser Lernalgorithmen für tief geschichtete Architekturen. Sie wurden intensiv erforscht, wobei unter anderem Methoden aus der Optimierung, der algebraischen Geometrie, der Kombinatorik, der Kodierungstheorie, der Polyedergeometrie und der Informationsgeometrie zum Einsatz kamen.
Nach erfolgreichem Training liefert eine RBM eine Darstellung in geschlossener Form für die den Trainingsdaten zugrundeliegende Verteilung. Es handelt sich um ein generatives Modell, das Stichproben aus der gelernten Verteilung ermöglicht, z. B. zur Erzeugung von Bildtexturen, insbesondere aus den relevanten Randverteilungen. So lassen sich beispielsweise bestimmte sichtbare Einheiten, die einer Teilbeobachtung entsprechen, fixieren, d. h., die entsprechenden sichtbaren Variablen werden auf die beobachteten Werte gesetzt und als Konstanten behandelt, während die übrigen sichtbaren Einheiten durch Stichprobenziehung bestimmt werden, um die Beobachtung zu vervollständigen.
Auf diese Weise können RBMs auch als Klassifikatoren eingesetzt werden: Die RBM wird darauf trainiert, die gemeinsame Wahrscheinlichkeitsverteilung von Eingaben (erklärenden Variablen) und den zugehörigen Labels (Zielvariablen oder Ausgabevariablen) zu modellieren, wobei beide durch die sichtbaren Einheiten der RBM repräsentiert werden. RBMs haben große Aufmerksamkeit bekommen, nachdem sie als Bausteine für mehrschichtige Lernarchitekturen, sogenannte Deep Belief Networks, vorgeschlagen wurden. Die Grundidee dieser tiefen Architekturen besteht darin, dass die verborgenen Neuronen einer trainierten RBM relevante Merkmale der Beobachtungen repräsentieren und diese Merkmale wiederum als Eingabe für eine weitere RBM dienen können. Durch das Stapeln von RBMs lassen sich Merkmale aus Merkmalen lernen, in der Hoffnung, zu einer abstrakten Repräsentation auf hoher Ebene zu gelangen.
Eine wichtige Eigenschaft ist, dass sowohl einzelne als auch gestapelte RBMs als deterministische Feedforward neural networks umgedeutet werden können. Betrachtet man sie als neuronale Netze, so fungieren sie als Abbildungen, welche die Beobachtungen auf die Erwartungswerte der latenten Variablen in der obersten Schicht übertragen. Diese lassen sich als die gelernten Merkmale interpretieren, die beispielsweise als Eingaben für ein System des überwachten Lernens dienen können. Zudem lässt sich das einem trainierten RBM oder Deep Belief Network entsprechende neuronale Netz um eine Ausgabeschicht erweitern, deren zusätzliche Einheiten Labels der Beobachtungen repräsentieren. Man erhält so ein herkömmliches neuronales Netz für Klassifikationsaufgaben oder Regressionsaufgaben, das mittels gängiger Algorithmen des überwachten Lernens weiter trainiert werden kann.

### Funktionsweise

Betrachtet wird ein Trainingssatz binärer Vektoren, bei denen es sich z. B. um Binärbilder handelt. Dieser Trainingssatz lässt sich mithilfe eines zweischichtigen Netzwerks modellieren. Darin sind stochastische, binäre Pixel über symmetrisch gewichtete Verbindungen mit stochastischen, binären Merkmalsdetektoren verknüpft. Die Pixel entsprechen den sichtbaren Einheiten der RBM, weil ihre Zustände beobachtet werden, während die Merkmalsdetektoren den versteckten Einheiten entsprechen. Eine gemeinsame Konfiguration 
$(v,h)$

 der sichtbaren und verborgenen Einheiten besitzt eine Energie, die wie folgt definiert ist:

$E(v,h)=-\sum _{i}a_{i}\cdot v_{i}-\sum _{j}b_{j}\cdot h_{j}-\sum _{i}\sum _{j}v_{i}\cdot h_{j}\cdot w_{i,j}$

wobei 
$v_{i}$

 und 
$h_{j}$

 die binären Zustände der sichtbaren Einheit 
$i$

 bzw. der verborgenen Einheit 
$j$

 sind, 
$a_{i}$

 und 
$b_{j}$

 deren Schwellenwerte darstellen und 
$w_{i,j}$

 das Gewicht zwischen ihnen bezeichnet. Über diese Energiefunktion weist das Netzwerk jedem möglichen Paar aus einem sichtbaren und einem verborgenen Vektor eine Wahrscheinlichkeit zu:

$p(v,h)={\frac {1}{Z}}\cdot \exp(-E(v,h))$

wobei die Partitionsfunktion 
$Z$

 durch die Summation über alle möglichen Paare sichtbarer und versteckter Vektoren gegeben ist:

$Z=\sum _{v}\sum _{h}\exp(-E(v,h))$

Die Wahrscheinlichkeit, die das Netzwerk einem sichtbaren Vektor 
$v$

 zuweist, ergibt sich aus der Summe über alle möglichen versteckten Vektoren:

$p(v)={\frac {1}{Z}}\cdot \sum _{h}\exp(-E(v,h))$

Weil die zugrundeliegende Struktur der RBM ein bipartiter Graph ist, d. h., es gibt keine Verbindungen innerhalb einer Schicht, sind die Aktivierungen der verborgenen Einheiten bei gegebenen Aktivierungen der sichtbaren Einheiten voneinander unabhängig. Umgekehrt sind die Aktivierungen der sichtbaren Einheiten bei gegebenen Aktivierungen der verborgenen Einheiten voneinander unabhängig. Das heißt, für 
$m$

 sichtbare Einheiten und 
$n$

 verborgene Einheiten ist die bedingte Wahrscheinlichkeit einer Konfiguration 
$v$

 der sichtbaren Einheiten, gegeben eine Konfiguration 
$h$

 der verborgenen Einheiten, gegeben durch

$p(v|h)=\prod _{i=1}^{m}P(v_{i}|h)$

Umgekehrt ist die bedingte Wahrscheinlichkeit von 
$h$

 bei gegebenem 
$v$

 gleich

$p(h|v)=\prod _{j=1}^{n}P(h_{j}|v)$

Die individuellen Aktivierungswahrscheinlichkeiten sind gegeben durch

$p(h_{j}=1|v)=\sigma \left(b_{j}+\sum _{i=1}^{m}w_{i,j}\cdot v_{i}\right)$
$p(v_{i}=1|h)=\sigma \left(a_{i}+\sum _{j=1}^{n}w_{i,j}\cdot h_{j}\right)$

wobei 
$\sigma (x)={\frac {1}{1+\exp(-x)}}$

 die logistische Funktion ist.
Die sichtbaren Einheiten einer RBM können multinomial sein, während die verborgenen Einheiten Bernoulli-verteilt sind. In diesem Fall wird die logistische Funktion für die sichtbaren Einheiten durch die Softmax-Funktion ersetzt:

$p(v_{i}^{k}=1|h)={\frac {\exp(a_{i}^{k}+\Sigma _{j}W_{ij}^{k}\cdot h_{j})}{\Sigma _{k'=1}^{K}\exp(a_{i}^{k'}+\Sigma _{j}W_{ij}^{k'}\cdot h_{j})}}$

wobei 
$K$

 die Anzahl der diskreten Werte ist, die die sichtbaren Einheiten annehmen.
Restricted Boltzmann Machines wurden zum kollaborativen Filtern auf Netflix eingesetzt.
