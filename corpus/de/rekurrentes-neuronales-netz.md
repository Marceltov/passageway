---
title: Rekurrentes neuronales Netz
url: https://de.wikipedia.org/wiki/Rekurrentes_neuronales_Netz
updated: '2025-07-05T12:46:44Z'
language: de
revision: '257632743'
license: CC BY-SA 4.0
source: Wikipedia
---

Als rekurrente bzw. rückgekoppelte neuronale Netze bezeichnet man neuronale Netze, die sich im Gegensatz zu den Feedforward-Netzen durch Verbindungen von Neuronen einer Schicht zu Neuronen derselben oder einer vorangegangenen Schicht auszeichnen. Im Gehirn ist dies die bevorzugte Verschaltungsweise neuronaler Netze, insbesondere im Neocortex. In künstlichen neuronalen Netzen wird die rekurrente Verschaltung von Modellneuronen benutzt, um zeitlich codierte Informationen in den Daten zu entdecken. Beispiele für solche rekurrenten neuronalen Netze sind das Elman-Netz, das Jordan-Netz, das Hopfield-Netz sowie das vollständig verbundene neuronale Netz.

## Eigenschaften

Ein rekurrentes neuronales Netz hat ein Gedächtnis, weil es Informationen aus früheren Eingaben verwendet, um die aktuelle Eingabe und Ausgabe zu beeinflussen. Während traditionelle tiefe neuronale Netze davon ausgehen, dass Eingaben und Ausgaben voneinander unabhängig sind, hängt die Ausgabe rekurrenter neuronaler Netze von den vorherigen Elementen innerhalb der Sequenz ab. Während zukünftige Ereignisse auch bei der Bestimmung der Ausgabe einer bestimmten Sequenz hilfreich wären, können unidirektionale rekurrente neuronale Netze diese Ereignisse nicht in ihren Vorhersagen berücksichtigen.
Ein weiteres Merkmal von rekurrenten Netzen besteht darin, dass sie Parameter über alle Schichten des Netzes hinweg gemeinsam nutzen. Während Feedforward-Netze über jeden Knoten unterschiedliche Gewichtungen haben, teilen sich rekurrente neuronale Netze innerhalb jeder Schicht denselben Gewichtungsparameter. Allerdings werden diese Gewichtungen immer noch durch die Prozesse der Backpropagation und des Gradientenabstiegs angepasst, um das bestärkende Lernen zu erleichtern.

## Typen von rekurrenten neuronalen Netzen

Rekurrente Netze lassen sich folgendermaßen unterteilen:

Bei einer direkten Rückkopplung (englisch direct feedback) wird der eigene Ausgang eines Neurons als weiterer Eingang genutzt.
Die indirekte Rückkopplung (englisch indirect feedback) verbindet den Ausgang eines Neurons mit einem Neuron der vorhergehenden Schichten.
Die seitliche Rückkopplung (englisch lateral feedback) verbindet den Ausgang eines Neurons mit einem anderen Neuron derselben Schicht.
Bei einer vollständigen Verbindung hat jeder Neuronenausgang eine Verbindung zu jedem anderen Neuron.
Praktische Anwendung finden rekurrente neuronale Netze bei Problemstellungen, die das Verarbeiten von Sequenzen erfordern. Beispiele dafür sind Handschrifterkennung, Spracherkennung und Maschinenübersetzung. Die hierbei vorherrschende Art der rekurrenten neuronalen Netze sind LSTMs beziehungsweise ähnliche Varianten, die auf einer direkten Rückkopplung basieren.
Die Implementierung von Rekurrenten neuronalen Netzen kann in gängigen Programmbibliotheken wie PyTorch bequem in Python erfolgen und dann mit Just-in-time-Kompilierung in effizienten Code übersetzt werden.

### Elman-Netz

Ein Elman-Netz ist ein einfaches rekurrentes künstliches neuronales Netz, das durch vorhandene Rückkopplungen von Kanten zwischen den künstlichen Neuronen in der Lage ist, zeitliche Abhängigkeiten von Eingaben implizit zu verarbeiten. Benannt ist diese Netz-Architektur nach Jeffrey L. Elman, der diese Struktur 1990 vorschlug.
Ein Elman-Netzwerk ist ein dreischichtiges neuronales Netz, dem man eine Menge von Kontexteinheiten hinzufügen kann. Die mittlere verborgene Schicht ist mit diesen Kontexteinheiten fest mit einer Gewichtung von 1 verbunden. Bei jedem Zeitschritt wird die Eingabe weitergeleitet und eine Lernregel angewendet. Die festen Rückverbindungen speichern eine Kopie der vorherigen Werte der versteckten Einheiten in den Kontexteinheiten, weil sie sich über die Verbindungen ausbreiten, bevor die Lernregel angewendet wird. Somit kann das Netzwerk eine Art Zustand aufrechterhalten, der es ihm ermöglicht, Aufgaben wie die Sequenzvorhersage auszuführen, die über die Leistungsfähigkeit eines standardmäßigen mehrlagiges Perzeptron hinausgehen.
Das System hat eine Eingangsschicht, eine verborgene Schicht und eine Ausgangsschicht, die alle in einer Feedforward-Weise verbunden sind. Die verborgene Schicht ist jedoch nicht nur mit der Ausgangsschicht verbunden, sondern in einer einfachen 1:1-Verbindung auch mit einer weiteren Schicht, der so genannten Kontextschicht. Um wiederkehrende Verbindungen zu bilden, wird die Ausgabe dieser Kontextschicht auch in die verborgene Schicht eingegeben. Mit Ausnahme dieser 1:1-Verbindungen von der verborgenen zur Kontextschicht, deren Gewichte auf 1 festgelegt sind, können alle anderen Schichten vollständig verbunden und alle Gewichte modifizierbar sein. Die wiederkehrenden Verbindungen der Kontextschicht stellen dem System ein Kurzzeitgedächtnis zur Verfügung. Die versteckten Einheiten beobachten nicht nur die eigentliche Eingabe, sondern erhalten über die Kontextschicht auch Informationen über ihren eigenen Zustand im letzten Zeitschritt. Da zu einem bestimmten Zeitschritt verborgene Einheiten bereits durch Eingaben in früheren Zeitschritten beeinflusst wurden, umfasst diese Wiederholung eine Erinnerung, die von früheren Zuständen abhängt, obwohl ihr Einfluss mit der Zeit abnimmt. Während des Betriebs wird der Eingang des Elman-Netzes mit einer zeitlichen Folge von Eingangsvektoren versehen. Um die Gewichte zu ändern, kann die Ausgabe mit einem gewünschten Ausgabevektor verglichen werden, und zum Beispiel kann die verallgemeinerte Delta-Regel angewendet werden, um die Gewichte zu ändern. Dadurch lernt das System, eine Ausgabe nicht nur direkt der Eingabe zuzuordnen, sondern auch der zeitlichen Abfolge mehrerer aufeinanderfolgender Eingabevektoren.

### Jordan-Netz

Jordan-Netze ähneln Elman-Netze. Die Kontexteinheiten werden von der Ausgangsschicht anstatt von der verborgenen Schicht gespeist. Die Kontexteinheiten in einem Jordan-Netz werden auch als Zustandsschicht bezeichnet. Sie haben eine wiederkehrende Verbindung zu sich selbst. Elman-Netze und Jordan-Netze sind auch als einfache rekurrente Netze bekannt.

## Pseudocode

Gegeben sei eine Zeitreihe x der Länge sequence_length.
Im rekurrenten neuronalen Netz gibt es eine Schleife, welche nacheinander alle Einträge der Zeitreihe x durch die Schichten neural_network verarbeitet. Diese haben als Rückgabewert in jedem Zeitschritt i sowohl die Vorhersage y_pred[i] als auch einen aktualisierten verdeckten Zustand hidden, welcher die Länge hidden_size hat. Als Resultat nach der Schleife wird die Sammlung aller Vorhersagen y_pred zurückgegeben.
Der folgende Pseudocode (angelehnt an die Programmiersprache Python) illustriert die Funktionsweise eines rekurrenten neuronalen Netzes.

Moderne Bibliotheken liefern laufzeitoptimierte Implementierungen der obigen Funktionalität oder erlauben die langsame Schleife durch Just-in-time-Kompilierung stark zu beschleunigen.

## Trainieren von rekurrenten neuronalen Netzen

Das Trainieren eines typischen rekurrenten neuronalen Netzes umfasst folgende Schritte:

Ein Beispiel aus einem Datensatz wird eingegeben.
Das Netz nimmt dieses Beispiel auf und wendet einige komplexe Berechnungen mit zufällig initialisierten Variablen an.
Ein vorhergesagtes Ergebnis wird produziert.
Der Vergleich dieses Ergebnis mit dem erwarteten Wert ergibt einen Fehler.
Wenn sich der Fehler durch denselben Pfad wieder ausbreitet, werden die Variablen angepasst.
Die Schritte werden wiederholt, bis die Variablen gut definiert sind.
Der Unterschied zu einem Feedforward-Netz ergibt sich aus der Tatsache, dass vor der Bewertung des Ergebnisses auch die vorherigen Eingaben bekannt sind. Rekurrente neuronale Netze können daher als mehrere neuronale Feedforward-Netze betrachtet werden und Informationen von einem zum anderen Netz weitergeben werden.
Rekurrente künstliche neuronale Netze sind schwierig durch Methoden des maschinellen Lernens zu trainieren. Ein populärer Ansatz ist es daher, nicht das Netz, sondern das Auslesen des Netzes zu trainieren. Das rekurrente neuronale Netz wird im Rahmen von Reservoir Computing als sogenanntes Reservoir betrachtet.
Im Falle von LSTMs werden die Netze durch Backpropagation-Through-Time (siehe Backpropagation) während des Trainingsvorgangs in ein Feedforward-Netz entsprechend der Sequenzlänge umgewandelt. Damit wird die Komplexität des Lernverhaltens ähnlich dem der herkömmlichen Feedforward-Netze.
Ausgangspunkt für die Backpropagation-Through-Time ist, dass die totale Verlustfunktion der Zeitreihe, welche aus 
$T$

 Zeitschritten besteht, wie folgt dargestellt werden kann:

$L=\sum _{t=1}^{T}l(y_{t},o_{t}(\theta ))$

,
wobei 
$l$

 eine Funktion ist, welche die Ausgabe (Output) des Netzwerkens 
$o_{t}$

 (zum Zeitpunkt 
$t$

) mit dem Ziel 
$y_{t}$

 vergleicht und wobei 
$\theta $

 der zeitinvariante Parametervektor des rekurrenten neuronalen Netzes ist.
Backpropagation-Through-Time erlaubt durch Anwenden der Kettenregel die Berechnung der (komponentenweisen) totalen Ableitung 
${\frac {dL}{d\theta _{i}}}$

. Da der Output 
$o_{t}(h_{t-1}(\theta ))$

 selbst von Werten 
$h_{t-1}$

 des vorherigen Zeitschrittes 
$t-1$

 abhängt und diese von 
$\theta $

, müssen diese vorherigen Zeitschritte in die Ableitung mit einbezogen werden.
Probleme beim Training von rekurrenten neuronalen Netzen können aufgrund von verschwindenden oder explodierenden Gradienten auftreten. Um diese Probleme zu umgehen, kann Teacher-Forcing angewendet werden, wobei man jedoch den Bias-Exposure tradeoff eingeht.

## Aktivierungsfunktion

Die am häufigsten verwendeten Aktivierungsfunktionen für rekurrente neuronale Netze sind:

Sigmoidfunktion: 
$g(z)={\frac {1}{1+e^{-z}}}$

Tangens hyperbolicus: 
$g(z)={\frac {\mathrm {e} ^{z}-\mathrm {e} ^{-z}}{\mathrm {e} ^{z}+\mathrm {e} ^{-z}}}$

Rectifier: 
$g(z)=\max(0,z)$

## Verlustfunktion

Um ein rekurrentes neuronales Netz zu trainieren, braucht man eine Möglichkeit, die Fehler zu messen, die es macht. Dafür kann man eine sogenannte Verlustfunktion definieren. Ziel ist es, die Parameter zu finden, die die Verlustfunktion für die Trainingsdaten minimieren.
Eine übliche Verlustfunktion ist die Kreuzentropie. Ist 
$n$

 die Anzahl der Trainingsbeispiele, dann ist die Verlustfunktion in Bezug auf die Vorhersagen 
$o_{n}$

 und die wahren Labels 
$y_{n}$

 gegeben durch

$L(y,o)=-{\frac {1}{n}}\sum _{i=1}^{n}y_{i}\log(o_{i})$

## Zielfunktionen

Mit einem geeigneten 
$P_{\theta }$

 fährt man fort, den Fehler aus den Zeitschritt zu minimieren und die Anpassung aus dem Aktualisierungsschritt zu maximieren. Dadurch wird jede Beobachtung des Ergebnisses 
$y(t)$

 zweimal verwendet. Der Wert des verborgenen Zustands vor einer Aktualisierung wir mit 
$z(t-)$

 bezeichnet und danach mit 
$z(t)$

. Die Verlustfunktion für den Prognoseschritt ist die negative logarithmische Wahrscheinlichkeit der Daten:

$L_{pred}(y_{i},\theta )=-\sum _{i=1}^{N}\sum _{t=t_{0,i}}^{T_{i}}\log(p_{\theta }(y|z(t-))$

Dabei ist 
$z(t-)$

 der endgültige Wert des verborgenen Zustands vor dem Aktualisierungsschritt. Die zusätzliche Verlustfunktion, um sicherzustellen, dass nach dem Aktualisierungsschritt die durch den neuen Wert des verborgenen Zustands implizierte Ergebnisverteilung nahe beim beobachteten Datenpunkt 
$y(t)$

 liegt, ist

$L_{jump}(y_{i},\theta )=-\sum _{i=1}^{N}\sum _{t=t_{0,i}}^{T_{i}}m_{i}\log(p_{\theta }(y|z(t))$

Dabei ist 
$m_{i}$

 eine binäre Maske, die nützlich ist, wenn ein Aktualisierungsschritt erforderlich ist, z. B. aufgrund von Änderungen in 
$z(t)$

, 
$y(t)$

 jedoch entweder nicht gemessen wird oder aus anderen Gründen fehlt. Wenn der Beobachtungsprozess mit Fehlern gemessen wird, können wir dies durch die Verwendung einer Kullback-Leibler-Divergenz als Verlustfunktion beschreiben:

$L_{jump}(y_{i},\theta )=-\sum _{i=1}^{N}KL(p_{\theta }(y|z(t)||p_{obs}(y,\sigma ^{2})))$

Dabei ist 
$p_{obs}(y,\sigma ^{2})$

 die angenommene Verteilung der Antwort 
$y(t)$

 bei gegebener Beobachtung 
$y$

 und der Annahme eines mittleren Messfehlers von Null mit Varianz 
$\sigma ^{2}$

.

## GloVe Modell

Das GloVe Modell ist eine Worteinbettungstechnik, die eine Co-Occurence-Matrix 
$X$

 verwendet, wobei jedes 
$X_{i,j}$

 die Anzahl der Male bezeichnet, in denen ein Ziel 
$i$

 mit einem Kontext 
$j$

 aufgetreten ist. Die Kostenfunktion 
$J$

 für dieses Modell lautet

$J(\theta )={\frac {1}{2}}\sum _{i,j=1}^{|V|}f(X_{i,j})(\theta _{i}^{T}e_{j}+b_{i}+b_{j}'-\log(X_{i,j}))^{2}$

wobei 
$f$

 eine Gewichtungsfunktion ist, sodass 
$f(X_{i,j})=0$

 für alle 
$X_{i,j}=0$

 ist.
