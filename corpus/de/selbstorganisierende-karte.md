---
title: Selbstorganisierende Karte
url: https://de.wikipedia.org/wiki/Selbstorganisierende_Karte
updated: '2026-08-09T04:39:37Z'
language: de
revision: '269503413'
license: CC BY-SA 4.0
source: Wikipedia
---

Als Selbstorganisierende Karten, Kohonenkarten oder Kohonennetze (nach Teuvo Kohonen; englisch self-organizing map, SOM bzw. self-organizing feature map, SOFM) bezeichnet man eine Art von künstlichen neuronalen Netzen. Sie sind als unüberwachtes Lernverfahren ein leistungsfähiges Werkzeug des Data-Mining. Ihr Funktionsprinzip beruht auf der biologischen Erkenntnis, dass viele Strukturen im Gehirn eine lineare oder planare Topologie aufweisen. Die Signale des Eingangsraums, z. B. visuelle Reize, sind jedoch multidimensional.
Es stellt sich also die Frage, wie diese multidimensionalen Eindrücke durch planare Strukturen verarbeitet werden. Biologische Untersuchungen zeigen, dass die Eingangssignale so abgebildet werden, dass ähnliche Reize nahe beieinander liegen. Der Phasenraum der angelegten Reize wird also kartiert.
Wird nun ein Signal an diese Karte herangeführt, so werden nur diejenigen Gebiete der Karte erregt, die dem Signal ähnlich sind. Die Neuronenschicht
wirkt als topologische Merkmalskarte, wenn die Lage der am stärksten erregten Neuronen in gesetzmäßiger und stetiger Weise mit wichtigen Signalmerkmalen korreliert ist.
Anwendung finden selbstorganisierende Karten zum Beispiel in der Computergrafik (als Quantisierungsalgorithmus zur Farbreduktion von Rastergrafikdaten) und zur Clusteranalyse.

## Laterale Umfeldhemmung

Ein allgemeines Arbeitsprinzip des Nervensystems ist, dass aktive lokale Gruppen von Nervenzellen andere Gruppen ihrer Umgebung hemmen, und somit deren Aktivität unterdrücken (siehe laterale Hemmung). Die Aktivität einer Nervenzelle wird daher aus der Überlagerung des erregenden Eingangssignals und den hemmenden Beiträgen aller Schichtneuronen bestimmt.
Da diese laterale Hemmung überall gilt, kommt es zu einem ständigen Wettbewerb um die Vorherrschaft. Der Verlauf der lateralen Hemmung ist für kurze Distanzen erregend/verstärkend und für lange Distanzen hemmend/schwächend. Es lässt sich zeigen, dass dieser Effekt ausreichend ist, eine Lokalisierung der Erregungsantwort in der Nähe der maximalen äußeren Erregung zu bewirken.

## Struktur und Lernen

Eine Eingabeschicht mit 𝑛 Neuronen ist vollständig mit allen Neuronen innerhalb der Kohonenkarte (der sogenannte competitive layer), im Folgenden einfach Karte, verbunden. Jeder zu kartierende Eingangsreiz 𝑣 wird über die Verbindungen an jedes Neuron dieser Karte weitergegeben.
Die Verbindungsgewichte 𝑤 zwischen den Neuronen der Eingabeschicht und den Neuronen in der Karte definieren je einen Punkt im Eingangsraum der angelegten Reize 𝑣. Alle Neuronen innerhalb der Karte sind untereinander inhibitorisch (hemmend) vernetzt.

Die Abbildung zeigt einen Adaptionsschritt im Modell von Kohonen. Ein Reiz 𝑣 wird an das Netz angelegt.
Das Netz sucht das Erregungszentrum 𝑠 in der Karte, dessen Gewichtsvektor 𝑤 am nächsten zu 𝑣 liegt (kleinster Abstand).
Der Unterschied zwischen 𝑤 und 𝑣 wird in einem Adaptionsschritt verringert.
Die Neuronen nahe am Erregungszentrum 𝑠 werden auch adaptiert, aber umso weniger, je weiter sie vom Erregungszentrum entfernt sind.
Es ist gebräuchlich, aber nicht zwingend, sowohl für die Lernvektoren als auch für die Karte den euklidischen Abstand als Abstandsmaß zu verwenden.
Steht ein Satz verschiedener Trainingsdaten zur Verfügung, so ist eine Epoche im Training vollständig, wenn alle Reize genau einmal in zufälliger Reihenfolge an die Eingabeschicht angelegt worden sind. Das Training endet, wenn das Netz seinen stabilen Endzustand erreicht hat.
Das Lernen in einer selbstorganisierten Karte kann formal als iterativer Prozess beschrieben werden. Im Anfangszustand sind die Gewichtsvektoren der Neuronen zufällig im Netz verteilt und in jedem Lernschritt wird an das Netz ein Reiz angelegt. Die selbstorganisierende Karte verändert die Gewichtsvektoren der Neuronen entsprechend der Hebbschen Lernregel, sodass sich im Laufe der Zeit eine topografische Abbildung ergibt.

## Training einer SOM im Beispiel

Die folgende Tabelle zeigt ein Netz, dessen Neuronen in einem Gitter angeordnet sind und zu Beginn zufällig
im Raum verteilt sind. Es wird mit Eingabereizen aus dem Quadrat trainiert, die gleichverteilt sind.

## Formale Beschreibung des Trainings

Gegeben ist eine endliche Menge M von Trainingsstimuli mi, die durch einen n-dimensionalen Vektor xi spezifiziert sind:

$M=\{m_{i}=(x_{i})\mid x_{i}\in X\subseteq \mathbb {R} ^{n},i=1,...,\mu _{M}\}$

Weiterhin sei eine Menge von μN Neuronen gegeben, denen jeweils ein Gewichtsvektor wi in X und eine Position ki auf einer Kohonen-Karte zugeordnet wird, die im Weiteren als zweidimensional angenommen wird. Die Kartendimension kann beliebig-dimensional gewählt werden, wobei Kartendimensionen kleiner-gleich drei zur Visualisierung von hochdimensionalen Zusammenhängen verwendet werden. Die Positionen auf der Karte sollen diskreten, quadratischen Gitterpunkten entsprechen (alternative Nachbarschaftstopologien wie z. B. hexagonale Topologien sind ebenfalls möglich), und jeder Gitterpunkt soll durch genau ein Neuron besetzt sein:

$N=\{n_{i}=(w_{i},k_{i})\mid w_{i}\in X\subseteq \mathbb {R} ^{n},k_{i}\in K^{2},i=1,...,\mu _{N}\}$

In der Lernphase wird aus der Menge der Stimuli zum Präsentationszeitpunkt t ein Element mjt gleichverteilt zufällig ausgewählt. Dieser Stimulus legt auf der Karte ein Gewinnerneuron nst fest, das als Erregungszentrum bezeichnet wird. Es handelt sich dabei um genau das Neuron, dessen Gewichtsvektor wst den geringsten Abstand im Raum X zu dem Stimulusvektor xjt besitzt, wobei eine Metrik dX(.,.) des Inputraumes gegeben sei:

$d_{X}(x_{j}^{t},w_{s}^{t})=min\{d_{X}(x_{j}^{t},w_{i}^{t})\mid i=1,...,\mu _{N}\}$

Nachdem nst ermittelt wurde, werden alle Neuronen nit bestimmt, die neben dem Erregungszentrum ihre Gewichtsvektoren anpassen dürfen. Es handelt sich dabei um die Neuronen, deren Entfernung dA(ks, ki) auf der Karte nicht größer ist als ein zeitabhängiger Schwellenwert, der als Entfernungsreichweite δt bezeichnet wird, wobei eine Metrik dA(.,.) der Karte gegeben sei. Diese Neuronen werden in einer Teilmenge N+t ⊂ Nt zusammengefasst:

$N^{+t}=\{n_{i}=(w_{i},k_{i})\mid d_{A}(k_{s},k_{i})\leq \delta ^{t}\}$

Im folgenden Adaptionsschritt wird auf alle Neuronen aus N+t ein Lernschritt angewendet, der die Gewichtsvektoren verändert. Der Lernschritt ist interpretierbar als eine Verschiebung der Gewichtsvektoren in Richtung des Stimulusvektors xjt.
Es wird entsprechend dem Modell von Ritter et al. (1991) dabei die folgende Adaptionsregel verwendet:

$w_{s}^{t+1}=w_{s}^{t}+\varepsilon ^{t}\cdot h_{si}^{t}\cdot (x_{j}-w_{s}^{t})$

mit den zeitabhängigen Parametergleichungen εt und hsit, die festgelegt werden als:
1) Die zeitabhängige Lernrate εt:

$\varepsilon ^{t}=\varepsilon _{\text{start}}\cdot \left({\frac {\varepsilon _{\text{end}}}{\varepsilon _{\text{start}}}}\right)^{\frac {t}{t_{\text{max}}}}$

mit der Startlernrate εstart und εend als der Lernrate zum Ende des Verfahrens, d. h. nach tmax Stimuluspräsentationen.
2) Die zeitabhängige Entfernungsgewichtungsfunktion hsit:

$h_{si}^{t}=e^{\frac {-d_{A}(k_{s},k_{i})^{2}}{2\cdot (\delta ^{t})^{2}}}$

mit δt als dem Nachbarschafts- oder Adaptionsradius um das Gewinner-Neuron auf der Karte:

$\delta ^{t}=\delta _{\text{start}}\cdot \left({\frac {\delta _{\text{end}}}{\delta _{\text{start}}}}\right)^{\frac {t}{t_{\text{max}}}}$

mit dem Adaptionsradius δstart zum Anfang des Verfahrens, und δend als dem Adaptionsradius zum Ende des Verfahrens.
Damit eine topologie-erhaltende Abbildung entsteht, d. h., dass benachbarte Punkte im Inputraum X auf benachbarte Punkte auf der Karte abgebildet werden, müssen zwei Faktoren berücksichtigt werden:

Die topologische Nachbarschaft hsit um das Erregungszentrum muss anfangs groß gewählt und im Laufe des Verfahrens verkleinert werden.
Die Adaptionsstärke εt muss ausgehend von einem großen Wert im Laufe des Verfahrens auf einen kleinen Restwert sinken.
In dem dargestellten Lernprozess werden tmax Präsentationen durchgeführt, wonach die SOM in die Anwendungsphase überführt werden kann, in der Stimuli präsentiert werden, die in der Lernmenge nicht vorkamen. Ein solcher Stimulus wird dem Gewinnerneuron zugeordnet, dessen Gewichtsvektor die geringste Distanz von dem Stimulusvektor besitzt, sodass dem Stimulus über den Umweg des Gewichtsvektors ein Neuron und eine Position auf der Neuronenkarte zugeordnet werden kann. Auf diese Weise wird der neue Stimulus automatisch klassifiziert und visualisiert.

## Varianten der SOM

Es wurden eine Vielzahl von Varianten und Erweiterungen zu dem ursprünglichen Modell von Kohonen entwickelt, u. a.:

Kontext-SOM (K-SOM)
Temporäre SOM (T-SOM)
Motorische SOM (M-SOM)
Neuronen-Gas (NG-SOM)
Wachsende selbstorganisierende Karte (GSOM)
Time Adaptive Self-Organizing Map (TASOM)
Wachsende Zellstrukturen (GCS-SOM)
Wachsende Gitterstruktur (GG-SOM)
Wachsende hierarchische SOM (GH-SOM)
Wachsendes Neuronen-Gas (GNG-SOM)
Parametrische SOM (P-SOM)
Hyperbolische SOM (H-SOM)
Interpolierende SOM (I-SOM)
Local-Weighted-Regression-SOM (LWR-SOM)
Selektive-Aufmerksamkeits-SOM (SA-SOM)
Gelernte Erwartungen in GNG-SOMs (LE-GNG-SOM)
Fuzzy-SOM (F-SOM)
Adaptive-Subraum-SOM (AS-SOM)
Generative Topographische Karte (GTM)

### Wachsende selbstorganisierende Karte

Die wachsende selbstorganisierende Karte (GSOM) ist eine erweiterbare Variante der selbstorganisierenden Karte, die entwickelt wurde, um das Problem der vorab festzulegenden Kartengröße bei klassischen SOMs zu umgehen. Während bei einer herkömmlichen selbstorganisierenden Karte die Anzahl und Anordnung der Neuronen vor dem Training meist festgelegt werden muss, beginnt die GSOM mit einer sehr kleinen Ausgangsstruktur und wächst während des Lernprozesses dynamisch an den Stellen, an denen die Daten eine feinere Auflösung erfordern. Dadurch kann die Karte die Verteilung der Eingabedaten flexibler und oft auch effizienter abbilden.
Das Wachstumsprinzip der GSOM basiert darauf, dass für jeden Knoten ein Fehlerwert akkumuliert wird, der angibt, wie stark die Eingaben von diesem Knoten nicht ausreichend repräsentiert werden. Überschreitet dieser Fehlerwert einen festgelegten Wachstumsschwellenwert, werden neue Knoten ergänzt, typischerweise an Randpositionen oder Grenzpositionen der Karte. Die Gewichte der neu erzeugten Knoten werden aus den Nachbarknoten initialisiert, damit sich die Struktur ohne abrupte Sprünge in die bestehende Karte einfügt. Auf diese Weise kann sich das Netz schrittweise an komplexe Datenverteilungen anpassen.
Wie bei der klassischen SOM wird auch die GSOM im Allgemeinen mit unüberwachtem Lernen trainiert: Für jeden Eingabevektor wird zunächst der Best Matching Unit bestimmt, also der Knoten mit der kleinsten Distanz zum Eingabemuster. Anschließend werden nicht nur dieser Gewinner, sondern auch seine Nachbarn in Richtung des Eingabewerts angepasst. Zusätzlich enthält die GSOM einen Wachstumsmechanismus, der es erlaubt, neue Knoten nur dort einzufügen, wo die vorhandene Auflösung nicht ausreicht. Dadurch eignet sich das Verfahren insbesondere für Datenmengen, bei denen die geeignete Netzgröße im Voraus schwer abzuschätzen ist.
Die GSOM ist eine Erweiterung der SOM, die zwei Ziele miteinander verbindet: erstens die topologieerhaltende Projektion hochdimensionaler Daten auf eine niedrigdimensionale Karte und zweitens eine adaptive Anpassung der Kartengröße an die Datenstruktur. Je nach gewähltem Wachstumsparameter kann die resultierende Karte stärker komprimiert oder stärker ausgedehnt werden, was die Granularität der Repräsentation beeinflusst. Damit gehört die GSOM zu den Verfahren, die die klassische SOM nicht ersetzen, sondern um eine adaptive Modellkomponente ergänzen.

### Time Adaptive Self-Organizing Map

Die Time Adaptive Self-Organizing Map (TASOM) ist eine Erweiterung der selbstorganisierenden Karte, die speziell für nichtstationäre Eingabedaten und sich verändernde Umgebungen entwickelt wurde. Im Unterschied zur klassischen SOM werden Lernrate und Nachbarschaftsbreite nicht global, sondern für jedes Neuron individuell und adaptiv angepasst. Dadurch kann das Netz auf neue Daten reagieren, ohne für jede Veränderung neu initialisiert werden zu müssen.
Ein wesentliches Merkmal von TASOM ist, dass jedes Neuron eigene Adaptionsparameter besitzt. Für den Gewinnerknoten und seine Nachbarn werden Lernrate und Nachbarschaftsmaß anhand der aktuellen Eingabe fortgeschrieben; zusätzlich wird in der Originalarbeit ein Skalierungsvektor verwendet, um Skalierungstransformationen des Eingaberaums auszugleichen. TASOM wurde unter anderem für Klassifikationsaufgaben und adaptive Datenanalyse eingesetzt.
