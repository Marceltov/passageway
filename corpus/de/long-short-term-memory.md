---
title: Long short-term memory
url: https://de.wikipedia.org/wiki/Long_short-term_memory
updated: '2026-01-09T21:55:01Z'
language: de
revision: '263188484'
license: CC BY-SA 4.0
source: Wikipedia
---

Long short-term memory (LSTM, deutsch: langes Kurzzeitgedächtnis) ist in der Informatik eine Technik, die zur Verbesserung der Entwicklung von künstlicher Intelligenz wesentlich beigetragen hat.
Beim Trainieren von künstlichen neuronalen Netzen werden Verfahren des Gradientenabstiegs genutzt, die man sich wie die Suche eines Bergsteigers nach dem tiefsten Tal vorstellen kann. Beim Deep Learning kann dies zu kurz greifen, so wie ein vergesslicher Bergsteiger beim Abstieg im ersten besten Tal landet und sein Dorf in einem tieferen Tal nicht finden kann. Das LSTM-Verfahren löst dieses Problem, indem es für eine LSTM-Zelle zur besseren Erinnerung drei Torsorten verwendet: Ein Eingangstor (Input Gate), ein Merk- und Vergesstor (Forget Gate) und ein Ausgangstor (Output Gate). LSTM ermöglicht auf diese Weise im Gegensatz zu herkömmlichen rekurrenten neuronalen Netzen eine Art Erinnerung an frühere Erfahrungen: Ein Kurzzeitgedächtnis, das lange anhält, weil das prinzipielle Verhalten des Netzes in den Gewichten kodiert ist.
1997 wurden LSTM-Netze von Sepp Hochreiter und Jürgen Schmidhuber in einer Veröffentlichung vorgestellt. Die Idee zu LSTM-Netzen geht jedoch auf die Diplomarbeit von Sepp Hochreiter im Jahr 1991 zurück. Schließlich wurden LSTMs 1999 von Felix Gers, Schmidhuber, und Fred Cummins verbessert. Seit etwa 2016 feiert LSTM bedeutende Erfolge, da seitdem große Datenmengen zum Training genutzt werden können, weitere Verbesserungen der LSTM-Technik durchgeführt wurden, hinreichend leistungsfähige Rechner zur Verfügung stehen und Grafikprozessor-Programmierung angewendet wird.
Neuronale Netze mit vielen Schichten sind extrem lernfähig. LSTM sorgt dafür, dass genau solche mehrschichtigen Netze gut funktionieren können. Dies hat einen Durchbruch bei der künstlichen Intelligenz ermöglicht.

## Verschwindender oder explodierender Gradient

Eine Möglichkeit, künstliche neuronale Netze zu trainieren, ist die Fehlerrückführung. In der frühen Trainingsphase macht ein Netz beispielsweise bei der Mustererkennung manches falsch: Auf einem Bild mit Katze soll eine Katze erkannt werden und kein Hund. Zur Korrektur des Fehlers werden die Auslöser der Abweichungen (Fehler) zwischen erzeugter Zuordnung (Hund) und Lösungszuordnung (Katze) zurückverfolgt und wiederholt steuernde Faktoren (Gewichte) in den Schichten des Netzes jeweils so verändert, dass die Zuordnungsfehler kleiner und kleiner werden. Im sogenannten Gradientenverfahren wird dieser Fehler minimiert: Die Zahlen in den steuernden Gewichten werden neu justiert.
Neuronale Netze bestehen aus hintereinandergeschalteten Modulen, die klassischerweise jeweils nur eine einzige Aktivierungsfunktion besitzen, die dafür sorgt, dass die Ausgabe zwischen 0 und 1 liegt. Bei jeder Fehlerkorrektur wird das Fehlersignal durch die Ableitung der Aktivierungsfunktion bestimmt. Durch diese Ableitung wird die Abstiegssteigung und die Richtung bestimmt, mit der das Fehlertal ermittelt wird.
Sepp Hochreiter erkannte 1991, dass dieses bis dahin übliche Verfahren bei mehrschichtigen Netzen ungeeignet ist. Je weiter nämlich der Fehler im Prozess (von hinten nach vorne gesehen) berechnet wird, desto öfter wird der Skalierungsfaktor mit dem Fehlerterm multipliziert. Wenn der Faktor (hier der Spektralradius einer Gewichtsmatrix) stets kleiner als 1 ist, verschwindet der Fehler und führt zu ineffektiven Gewichtsaktualisierungen: Denn wenn Zahlen zwischen 0 und 1 miteinander multipliziert werden, so ist das Produkt kleiner als der größere der beiden Faktoren. Ein ursprünglich hoher Wert verschwindet also auf lange Sicht. Wenn die Faktoren andererseits größer als 1 wären, würde der Fehlerwert auf die Dauer explodieren.
Die Module in der Mitte des Netzes, sogenannte Hidden Layer, die der Eingabeschicht näher sind als der Ausgabeschicht, werden also bei der (rückwärts berechneten) Fehlerjustierung zu wenig berücksichtigt. Das führt dazu, dass sie kaum trainiert werden, so als wenn beim Fußball nur die Stürmer dazulernen, wenn es um das Toreschießen geht, nicht jedoch die Mittelfeldspieler oder Verteidiger.

## Drei Gates und eine innere Zelle

Um dieses Problem zu lösen, wurde ein LSTM-Modul entworfen, das einen relativ konstanten und anwendbaren Fehlerfluss ermöglicht. Man schaut sich genau an, welche Informationen in die innere Zelle hineinlaufen und hinauslaufen sollen. Das LSTM hat die Fähigkeit, Informationen zum Zellzustand zu entfernen oder hinzuzufügen, sorgfältig reguliert durch Strukturen, die Tore oder Gates genannt werden. LSTM-Module sind zwar ebenso wie herkömmliche Module kettenartig hintereinandergeschaltet, aber sie haben intern eine andere Struktur: Die zusätzlichen Gates sind eine Möglichkeit, Informationen optional durchzulassen.
Statt einer einzigen neuronalen Funktion im LSTM-Modul gibt es vier, die auf eine ganz besondere Art und Weise miteinander interagieren. Ein LSTM-Modul enthält die genannten drei Gates und eine innere Zelle. Kurz gesagt steuert

das Input Gate das Ausmaß, in dem ein neuer Wert in die Zelle fließt,
das Forget Gate das Ausmaß, in dem ein Wert in der Zelle verbleibt bzw. vergessen wird, und
das Output Gate das Ausmaß, in dem der Wert in der Zelle zur Berechnung für das nächste Modul der Kette verwendet wird.
Diese Netzelemente werden mit sigmoiden neuronalen Funktionen und diversen Vektor- und Matrixoperationen verbunden und ineinander überführt.

## Aufbau eines LSTM

Es gibt verschiedene Arten von LSTM-Architekturen. Üblich ist besonders bei der Bildverarbeitung das convolutionale LSTM-Netz, das hier skizziert wird. Es unterscheidet sich vom bloßen Peephole LSTM, das die Matrixmultiplikation verwendet, dadurch, dass die Aktivität jedes Neurons über eine diskrete Faltung (daher der Zusatz convolutional) berechnet wird. Intuitiv wird dabei schrittweise eine vergleichsweise kleine Faltungsmatrix (Filterkernel) über das Inputbild bewegt. Guckloch (Peephole) heißen diese Netze, weil die Gates den Zellstatus sehen können, also auch die Informationen aus der Zelle verarbeiten. Index t ist jeweils der aktuelle Durchlauf, t-1 bezeichnet den vorherigen Durchlauf. d und e sind jeweils die Anzahlen der Spalten und Zeilen von Vektoren und Matrizen.
Der Datenfluss zwischen den verschiedenen Gates und ihrer inneren Zelle ist durch Vektor- und Matrizenoperationen bestimmt. Zunächst wird hier die mathematische Struktur des Forget Gates beschrieben. 
$f_{t}$

 ist der dazugehörende e-stellige Aktivierungsvektor:

${\begin{aligned}f_{t}&=\sigma _{g}(W_{f}*x_{t}+U_{f}*h_{t-1}+V_{f}\circ c_{t-1}+b_{f})\\\end{aligned}}$

.

$x_{t}$

 ist der d-stellige Inputvektor. In der Kette aufeinander folgender Neuronen ist er (zusammen mit dem e-stelligen Outputvektor 
$h_{t-1}$

 des vorigen Durchlaufs) die Schnittstelle zum vorher in der Kette agierenden Neuron. Die drei Gewichtsmatrizen (weight matrices) 
$W,U,V$

 bilden den wertvollen Teil jedes Netzes, weil sie das Trainingswissen enthalten. 
$W$

 ist dabei eine e
$\times $

d-Matrix, 
$U$

 ist eine quadratische e
$\times $

e-Matrix und 
$V$

 ist ein e-stelliger Vektor. Zuletzt ist 
$b$

 der e-stellige Bias-Vektor. Wenn kein starker Input von anderen Einheiten erfolgt, dann stellt das Bias sicher, dass die Einheit bei starkem Gewicht aktiv bleibt und bei schwachem inaktiv. 
$\sigma _{g}$

 stellt eine Sigmoidfunktion der Gates dar, die nichtlinear Werte zwischen 0 und 1 aus dem Ganzen bildet.
Es gibt hier drei verschiedene Arten von Matrizenoperatoren:

+: Matrizenaddition

$\circ $

: Hadamard-Produkt (für die Gucklochinformationen des vorigen Durchlaufs)

$*$

: Matrizenmultiplikation.
Diese formelhaften Darstellungen erscheinen zwar kompliziert, aber das tatsächliche Rechnen übernehmen die jeweiligen Programmbibliotheken der Anbieter für KI.
Die Aktivierungsvektoren des Input Gates 
$i_{t}$

 und des Output Gates 
$o_{t}$

 entsprechen beide dem Aufbau des Forget Gate Vektors 
$f_{t}$

:

${\begin{aligned}i_{t}&=\sigma _{g}(W_{i}*x_{t}+U_{i}*h_{t-1}+V_{i}\circ c_{t-1}+b_{i})\\o_{t}&=\sigma _{g}(W_{o}*x_{t}+U_{o}*h_{t-1}+V_{o}\circ c_{t-1}+b_{o})\\\end{aligned}}$

Der Zellzustand ist so etwas wie ein Förderband. Die Information verläuft geradlinig über die gesamte Kette, mit nur geringen linearen Wechselwirkungen. Die innere Zelle mit dem Zellstatusvektor 
$c_{t}$

 hat folgenden Aufbau:

${\begin{aligned}c_{t}&=f_{t}\circ c_{t-1}+i_{t}\circ \sigma _{c}(W_{c}*x_{t}+U_{c}*h_{t-1}+b_{c})\\\end{aligned}}$

.
Für die Sigmoidfunktionen 
$\sigma _{c}$

 und 
$\sigma _{h}$

 wird üblicherweise der hyperbolische Tangens (auch: tanh) verwendet. 
$h_{t-1}$

 ist der Outputvektor (des vorigen Durchlaufs, nicht im groben Schaubild zu sehen):

${\begin{aligned}c_{t}&=f_{t}\circ c_{t-1}+i_{t}\circ \tanh(W_{c}*x_{t}+U_{c}*h_{t-1}+b_{c})\\\end{aligned}}$

Die Anfangswerte für 
$c_{0}$

 und 
$h_{0}$

 werden jeweils mit Nullvektoren initialisiert. Der Outputvektor berechnet sich folgendermaßen:

${\begin{aligned}h_{t}&=o_{t}\circ \sigma _{h}(c_{t})\end{aligned}}$

oder konkret mit dem Tangens hyperbolicus:

${\begin{aligned}h_{t}&=o_{t}\circ \tanh(c_{t})\end{aligned}}$

## Varianten und Alternativen

Bevor LSTMs sich allgemein durchsetzten, wurden verzögerte Netze, sogenannte Time Delay Neural Networks, verwendet, später Hidden Markov Models.
Seit ihren Anfängen kamen immer mehr Varianten des LSTM hinzu. Wie oben beschrieben wurde zusätzlich das Forget Gate und die Peepholetechnik entwickelt sowie die Faltungstechnik. LSTM-Netze werden insbesondere in der Spracherkennung für die Klassifikation von Phonemen eingesetzt. Die erste Arbeit, die sich mit der Klassifikation von Phonemen mittels LSTM befasst, wurde 2005 von Alex Graves und seinem Betreuer Schmidhuber veröffentlicht. Seit 2007 wurde LSTM für die Analyse und Erkennung kontinuierlicher Sprache eingesetzt. Forscher wie Haşim Sak und Wojciech Zaremba arbeiteten LSTM-Techniken für die akustische Modellierung und die Spracherkennung weiter aus.
Rupesh Kumar Srivastava, Klaus Greff und ihr Betreuer Schmidhuber schufen unter Verwendung der LSTM Prinzipien das „Highway network“, ein künstliches neuronales Netz mit Hunderten von Schichten, das somit viel tiefer war als frühere vorwärtsgerichtete Netzwerke. Sieben Monate später gewannen Kaiming He, Xiangyu Zhang, Shaoqing Ren und Jian Sun den ImageNet 2015 Wettbewerb mit einer Highway Network Variante namens Residual Network (ResNet). Letzteres wurde zum meistzitierten neuronalen Netz des 21. Jahrhunderts.
Eine beliebte LSTM-Variante, die von Gers und Schmidhuber eingeführt wurde, ist das Hinzufügen von „peephole connections“. Das bedeutet, dass die Schichten den Zustand betrachten und verarbeiten:

${\begin{aligned}f_{t}&=\sigma _{g}(W_{f}\cdot [c_{t-1},h_{t-1},x_{t}]+b_{f})\\i_{t}&=\sigma _{g}(W_{i}\cdot [c_{t-1},h_{t-1},x_{t}]+b_{i})\\o_{t}&=\sigma _{g}(W_{o}\cdot [c_{t},h_{t-1},x_{t}]+b_{o})\\\end{aligned}}$

Eine weitere Variante besteht darin, gekoppelte Forget Gates und Input Gates zu verwenden. Anstatt getrennt zu entscheiden, was vergessen und was mit neuen Werten ergänzt werden soll, wird diese Entscheidung gleichzeitig getroffen. Es werden genau dann neue Werte ergänzt, wenn ältere Werte vergessen werden:

${\begin{aligned}c_{t}&=f_{t}\circ c_{t-1}+(1-f_{t})\circ {\tilde {c_{t}}}\end{aligned}}$

Als Alternative zu LSTM wurden 2014 von Kyunghyun Cho und seinem Team Gated Recurrent Units entwickelt. Diese werden besonders bei der Musikmodellierung eingesetzt. Sie kombinieren das Forget Gate und das Input Gate zu einem einzigen Update Gate. Das resultierende Modell ist einfacher als herkömmliche LSTM-Modelle, und die Gates werden auf eine andere Art angeordnet. Die Vektor- und Matrixoperationen können folgendermaßen geschrieben werden:

${\begin{aligned}z_{t}&=\sigma _{g}(W_{z}\cdot [h_{t-1},x_{t}])\\r_{t}&=\sigma _{g}(W_{r}\cdot [h_{t-1},x_{t}])\\{\tilde {h_{t}}}&=\tanh(W\cdot [r_{t}*h_{t-1},x_{t}])\\h_{t}&=(1-z_{t})*h_{t-1}+z_{t}*{\tilde {h_{t}}}\\\end{aligned}}$

## Erfolge

In den Jahren nach 2010 verbesserte sich die technische Situation für LSTM außerordentlich: Die Einführung von Big Data stellte riesige Mengen von Daten zum Trainieren der Netze zur Verfügung. Der Boom von grafisch aufwendigeren Computerspielen führte zu immer besseren und günstigeren Grafikkarten. Auf diesen Grafikkarten können für die Grafikberechnungen sehr viele Matrixmultiplikationen gleichzeitig durchgeführt werden. Genau das braucht man für KI und LSTM. Schnelle GPU-Implementierungen dieser Kombination wurden 2011 durch Dan Ciresan und Kollegen in Schmidhubers Gruppe eingeführt. Sie gewannen seither zahlreiche Wettbewerbe, u. a. die „ISBI 2012 Segmentation of Neuronal Structures in Electron Microscopy Stacks Challenge“ und den „ICPR 2012 Contest on Mitosis Detection in Breast Cancer Histological Images“. Die CUDA-Schnittstelle von NVIDIA in Verbindung mit Grafikkarten desselben Herstellers wird hierfür am häufigsten verwendet, was wesentlich für den großen wirtschaftlichen Erfolg dieser Firma war. Google entwickelte alternativ zum Grafikprozessor Tensor Processing Units, um Anwendungen im Rahmen von maschinellem Lernen zu beschleunigen. Sie werden unter anderem angewendet, um effektiv LSTMs zu verarbeiten.
Seit etwa 2016 setzen große Technologieunternehmen wie Google, Apple und Microsoft LSTM als grundlegende Komponente für neue Produkte ein. So verwendete Google beispielsweise LSTM für die Spracherkennung auf dem Smartphone, für den Smart Assistant Allo und für Google Translate. Apple verwendet LSTM für die „Quicktype“-Funktion auf dem iPhone und für Siri. Amazon verwendet LSTM für Amazon Alexa.
LSTM wird heutzutage auch in der Landwirtschaft eingesetzt, z. B. um die Auswirkungen von Düngung vorherzusagen und Düngungsempfehlungen abzugeben.
Es gibt unzählige weitere LSTM-Anwendungen. Laut Google Scholar wurde LSTM allein im Jahre 2021 über 16000 mal zitiert. Dies spiegelt u. a. zahlreiche Anwendungen in der Medizin und im Gesundheitswesen wider.
