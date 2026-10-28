---
title: Hopfield-Netz
url: https://de.wikipedia.org/wiki/Hopfield-Netz
updated: '2026-07-14T12:52:37Z'
language: de
revision: '268779384'
license: CC BY-SA 4.0
source: Wikipedia
---

Als Hopfield-Netz bezeichnet man eine besondere Form eines künstlichen neuronalen Netzes, das sich von anderen künstlichen neuronalen Netzen dadurch unterscheidet, dass es ein rekurrentes neuronales Netz ist, das symmetrisch gewichtete Verbindungen besitzt und als Assoziativspeicher dient, der stabile Zustände (Attraktoren) für Muster erkennt. Es erkennt gespeicherte Muster anhand von Ähnlichkeiten, indem es sich in einen stabilen Zustand bewegt, der einem bekannten Muster entspricht.
Es ist nach dem amerikanischen Wissenschaftler John Hopfield benannt, der das Modell 1982 bekannt machte.
Hopfield-Netze hatten ursprünglich eine bedeutende Rolle in der Entwicklung der neuronalen Netzwerke, da sie als frühes Modell für assoziative Speicher und Mustererkennung dienten und wichtige Erkenntnisse zur Energie-Minimierung in neuronalen Netzen lieferten. Heute sind sie weiterhin von Bedeutung als Grundlage für moderne Ansätze in der künstlichen Intelligenz und maschinellem Lernen, insbesondere in der Forschung über rekurrente Netze und Energie-basierte Modelle.

## Struktur

Hopfield-Netze bestehen aus vollständig miteinander verbundenen Neuronen, bei denen jedes Neuron sowohl Eingaben von als auch Ausgaben an alle anderen Neuronen weiterleitet, wobei die Verbindungen symmetrisch sind.
Hopfield-Netze gehören zur Klasse der Feedback-Netze (Netze mit Rückkopplung).
Bei einem Hopfield-Netz existiert nur eine Schicht, die gleichzeitig als Ein- und Ausgabeschicht fungiert. Jedes der binären McCulloch-Pitts-Neuronen ist mit jedem anderen, ausgenommen sich selbst, verbunden. Die Neuronen können die Werte −1 und +1 annehmen, welche den Zuständen „feuert nicht“ und „feuert“ entsprechen.
In Hopfield-Netzwerken sind die synaptischen Gewichte symmetrisch, d. h. für alle i und j gilt:

$w_{i,j}=w_{j,i}$

.
Dies ist zwar biologisch nicht sinnvoll, erlaubt aber das Aufstellen einer Energiefunktion und die Analyse der Netzwerke mit Methoden der statistischen Mechanik.
Da für Ein- und Ausgabe dieselben künstlichen Neuronen verwendet werden, spricht man auch von einem Autoassoziationsnetz.

## Arbeitsweise

Die Arbeitsweise eines Hopfield-Netzes beruht darauf, dass es durch wiederholte Aktualisierung der Neuronen in einen stabilen Zustand übergeht, der einem gespeicherten Muster entspricht, wobei es durch Minimierung einer Energiefunktion Muster erkennt.
Bei der Implementierung eines Hopfieldnetzwerkes, also dabei eine programmierbare Form zu erstellen, stellt sich die Frage, ob
die Gewichte der Neuronen synchron oder asynchron geändert werden sollen.

synchrone Änderung bedeutet, dass in einem Iterationsschritt alle Neuronen gleichzeitig aktualisiert werden.
asynchrone Änderung bedeutet, dass ein Neuron zufällig gewählt und berechnet und der Wert bei der nächsten Berechnung sofort mit berücksichtigt wird.
Asynchrones Ändern des Hopfieldnetzes ist am verbreitetsten, weil es die Stabilität des Netzwerks schneller erreicht.
Die Eingabefunktion für jedes Neuron ist die gewichtete Summe der Ausgabe aller anderen Neuronen:

$f_{\mathrm {net} }^{\left(i\right)}(w,\mathrm {in} )=\sum _{i}{w_{i}\mathrm {in} _{i}}=\sum _{j\neq i}w_{ij}\mathrm {out} _{j}$

Die Aktivierungsfunktion jedes Neurons ist eine Schwellenfunktion:

$f_{\mathrm {act} }^{\left(i\right)}(\mathrm {net} _{i},\theta _{i})={\begin{cases}1&{\text{falls}}\ \mathrm {net} _{i}\geq \theta \\-1&\mathrm {sonst} \end{cases}}$

Die Ausgabefunktion jedes Neurons ist die identische Abbildung:

$f_{\mathrm {out} }^{\left(i\right)}(\mathrm {act} _{i})=\mathrm {act} _{i}$

Die alternative Aktivierungsfunktion ist

$f_{\mathrm {act} }^{\left(i\right)}(\mathrm {net} _{i},\theta _{i},\mathrm {act} _{i})={\begin{cases}1&{\text{falls}}\ \mathrm {net} _{i}>\theta \\-1&{\text{falls}}\ \mathrm {net} _{i}<\theta \\\mathrm {act} _{i}&{\text{falls}}\ \mathrm {net} _{i}=\theta \end{cases}}$

## Musterwiederherstellung mit Hopfieldnetzen

Hopfield-Netze können als Autoassoziativspeicher benutzt werden, um verrauschte oder auch nur teilweise vorhandene Muster zu rekonstruieren.
Dies geschieht in drei Phasen:

### Trainingsphase

Hier werden dem Netz eine Zahl L von vorgegebenen Mustern eingespeichert. Dies geschieht durch Einstellen der synaptischen Gewichte.
Gesucht ist also eine geeignete symmetrische Gewichtsmatrix der Größe 
$N\times N$

. Sie kann zum Beispiel in einem Schritt mit folgender Regel berechnet werden, die auch als verallgemeinerte Hebbsche Lernregel bezeichnet wird:

$w_{i,j}=w_{j,i}={\begin{cases}\sum \limits _{\mu =1}^{L}M_{\mu i}\cdot M_{\mu j}{\text{,}}&{\text{falls }}i\neq j\\0&{\text{sonst,}}\end{cases}}$

wobei

$L$

 die Anzahl der zu assoziierenden Muster,

$N$

 die Anzahl der Dimensionen eines Musters und

$M\in \mathbb {R} ^{L\times N}$

 die (unüberwachte) Lernaufgabe bezeichnen
Man möchte im Allgemeinen möglichst viele verschiedene Muster in ein Hopfield einspeisen. Jedoch ist die Speicherkapazität nach dem Verhältnis 
${\tfrac {L}{N}}$

 begrenzt.

### Eingeben eines Testmusters

Nun gibt man ein Testmuster, zum Beispiel ein verrauschtes oder unvollständiges Bild in das Netz hinein. Hierzu setzt man einfach die Neuronen in den Zustand, der dem Testmuster entspricht.

### Rechenphase

Die Neuronen werden asynchron mit folgender Regel aktualisiert:

$s_{i}=\left\{{\begin{array}{ll}1&{\text{wenn }}\sum _{j}{w_{ij}s_{j}}>\theta _{i},\\-1&{\text{sonst,}}\end{array}}\right.$

wobei 
$s_{i}$

 der Zustand des zu aktualisierenden Neurons und 
$\theta _{i}$

 ein Schwellenwert ist.
Das Ergebnis könnte in diesem Fall ein je nach Anzahl der Iterationsschritte mehr oder weniger
gut entrauschtes Bild sein. Bis zu einem Verhältnis 
${\tfrac {L}{N}}=0{,}138$

 (Verhältnis einzuspeichernder Muster zu Neuronen des Hopfield-Netzes) garantiert die Hebbsche Regel, dass das System sich nicht mehr ändert, wenn es in einem Zustand angelangt ist, der einem der gespeicherten Muster entspricht. Es lässt sich außerdem zeigen, dass das System immer in einem stabilen Endzustand ankommt.
Folgende drei Endzustände sind denkbar:

Das Muster wurde korrekt erkannt.
Das invertierte Muster wurde erkannt.
Es kann kein Muster erkannt werden, das Netzwerk gelangt in einen stabilen unechten Zustand, der keinem der Muster entspricht.

## Training eines Hopfield-Netzes

Das Training eines Hopfield-Netzes besteht darin, die Energie jener Zustände zu senken, die das Netz speichern soll. Dadurch kann das Netz als adressierbarer Speicher fungieren: Es konvergiert zu einem gespeicherten Zustand, selbst wenn ihm nur ein Teil dieses Zustands vorgegeben wird. Das Netz lässt sich nutzen, um aus einer verfälschten Eingabe jenen trainierten Zustand wiederherzustellen, der der Eingabe am ähnlichsten ist. Man spricht hierbei von assoziativem Gedächtnis, da gespeicherte Informationen auf der Grundlage von Ähnlichkeit abgerufen werden.

### Lernregeln

Es gibt verschiedene Lernregeln, mit denen Informationen im Gedächtnis eines Hopfield-Netzwerks gespeichert werden können. Es ist wünschenswert, dass eine Lernregel die folgenden Eigenschaften aufweist:

Lokal: Eine Lernregel ist lokal, wenn jedes Gewicht unter Verwendung von Informationen aktualisiert wird, die den Neuronen an beiden Enden der jeweiligen Verbindung der das Gewicht zugeordnet ist zur Verfügung stehen.
Inkrementell: Neue Muster können gelernt werden, ohne auf Informationen aus den bereits für das Training verwendeten alten Mustern zurückzugreifen. Das bedeutet: Wenn ein neues Muster für das Training genutzt wird, hängen die neuen Gewichtswerte lediglich von den alten Werten und dem neuen Muster ab.
Diese Eigenschaften sind erstrebenswert, weil eine Lernregel, die sie erfüllt, biologisch plausibler ist. Da das menschliche Gehirn beispielsweise ständig neue Konzepte lernt, lässt sich schlussfolgern, dass menschliches Lernen inkrementell erfolgt. Ein nicht-inkrementelles Lernsystem würde hingegen im Allgemeinen nur ein einziges Mal mit einer riesigen Menge an Trainingsdaten trainiert werden.

### Hebbsche Lernregel

Die Hebbsche Lernregel wurde von Donald Hebb eingeführt, um das assoziative Lernen zu erklären, bei dem die gleichzeitige Aktivierung von Neuronen zu einer deutlichen Zunahme der synaptischen Stärke zwischen diesen Zellen führt. Oft wird sie mit dem Satz zusammengefasst: „Neuronen, die gemeinsam feuern, verbinden sich miteinander. Neuronen, die nicht synchron feuern, bilden keine Verbindung aus.“
Die Hebbsche Lernregel ist sowohl lokal als auch inkrementell. Bei Hopfield-Netzen wird sie beim Lernen von 
$n$

 binären Mustern folgendermaßen implementiert:

$w_{i,j}={\frac {1}{n}}\sum _{\mu =1}^{n}\epsilon _{i}^{\mu }\epsilon _{j}^{\mu }$

wobei 
$\epsilon _{i}^{\mu }$

 für das Bit i aus dem Muster 
$\mu $

 steht. Wenn die den Neuronen i und j entsprechenden Bits im Muster 
$\mu $

 gleich sind, ist das Produkt 
$\epsilon _{i}^{\mu }\epsilon _{j}^{\mu }$

 positiv. Dies wiederum wirkt sich positiv auf das Gewicht 
$w_{i,j}$

 aus, und die Werte von i und j tendieren dazu, einander anzugleichen. Das Gegenteil geschieht, wenn die den Neuronen i und j entsprechenden Bits unterschiedlich sind.

### Stokey-Lernregel

Diese Regel wurde von Amos Storkey eingeführt und ist sowohl lokal als auch inkrementell. Storkey zeigte zudem, dass ein mit dieser Regel trainiertes Hopfield-Netz eine höhere Kapazität aufweist als ein entsprechendes, mit der Hebbschen Lernregel trainiertes Netz. Man sagt, die Gewichtsmatrix eines Attraktor-Neuronennetzes folge der Storkey-Lernregel, wenn sie folgende Bedingung erfüllt:

$w_{i,j}^{\nu }=w_{i,j}^{\nu -1}+{\frac {1}{n}}\epsilon _{i}^{\nu }\epsilon _{j}^{\nu }-{\frac {1}{n}}\epsilon _{i}^{\nu }h_{j,i}^{\nu }-{\frac {1}{n}}\epsilon _{j}^{\nu }h_{i,j}^{\nu }$

wobei 
$h_{i,j}^{\nu }=\sum _{k=1:i\neq k\neq j}^{n}w_{i,k}^{\nu -1}\epsilon _{k}^{\nu }$

 eine Form eines lokalen Feldes am Neuron i ist.
Diese Lernregel ist lokal, da die Synapsen nur die Neuronen in ihrer unmittelbaren Umgebung berücksichtigen. Aufgrund des Einflusses des lokalen Feldes nutzt die Regel mehr Informationen aus den Mustern und Gewichten als die verallgemeinerte Hebbsche Lernregel.

## Kapazität

Die Netzwerkkapazität des Hopfield-Netzwerkmodells wird durch die Anzahl der Neuronen und die Verbindungen innerhalb des jeweiligen Netzwerks bestimmt. Somit hängt die Anzahl der speicherbaren Informationen von der Anzahl der Neuronen und Verbindungen ab. Es wurde gezeigt, dass die Abrufgenauigkeit bei einem Verhältnis von Vektoren zu Knoten bei 0,138 lag. Das heißt, pro 1000 Knoten können etwa 138 Vektoren aus dem Speicher abgerufen werden.
Es ist daher offensichtlich, dass beim Versuch, eine große Anzahl von Vektoren zu speichern, häufig Fehler auftreten. Wenn das Hopfield-Modell nicht das korrekte Muster abruft, kann dies auf eine sogenannte Intrusion (Eindringen eines falschen Elements) zurückzuführen sein. Weil semantisch verwandte Elemente zur Verwechslung führen können, wird mitunter ein falsches Muster abgerufen. Das Hopfield-Netzwerkmodell neigt also dazu, beim Abruf ein gespeichertes Element mit einem anderen zu verwechseln. Durch die Storkey-Lernmethode lassen sich eine fehlerfreie Wiedergabe sowie eine hohe Kapazität von über 0,14 im Netzwerk erzielen. Später wurden weitere, vom Hopfield-Netzwerk inspirierte Modelle entwickelt, um die Speicherkapazität zu erhöhen und die Fehlerrate beim Abruf zu senken. Einige dieser Modelle ermöglichen zudem das sogenannte One Shot Learning (Lernen aus einem einzigen Durchgang).
Die Speicherkapazität bei Anwendung der Hebbschen Lernregel beträgt 
$C\cong {\frac {n}{2\cdot \ln(n)}}$

, wobei 
$n$

 die Anzahl der Neuronen im Netz ist.
Die Speicherkapazität bei Anwendung der Stokey-Lernregel beträgt 
$C\cong {\frac {n}{\sqrt {2\cdot \ln(n)}}}$

, wobei 
$n$

 die Anzahl der Neuronen im Netz ist.

## Diskrete Hopfield-Netze

Diskrete Hopfield-Netze ist eine Art von Algorithmus, die als autoassoziative Erinnerungen bezeichnet werden. Sie können nützliche Informationen speichern und diese Informationen später aus teilweise gebrochenen Mustern reproduzieren. Autoassoziative Erinnerungen sind ein mögliches Modell, um Funktionen des Gedächtnisses in einem neuronalen Netzwerkmodell abzubilden.
Das Netzwerk arbeitet nur mit binären Vektoren. Aber für dieses Netzwerk werden keine Binärzahlen in einer typischen Form verwendet. Stattdessen verwendet man bipolare Zahlen. Sie sind fast gleich, aber anstelle von 0 verwendet man −1, um einen negativen Zustand zu decodieren. Grundsätzlich sind bipolare Vektoren eher orthogonal zueinander, was ein kritischer Moment für das diskrete Hopfield-Netz ist.
Dichte assoziative Erinnerungen ermöglichen die Speicherung und den zuverlässigen Abruf einer exponentiell großen Anzahl von Erinnerungen. Diese Modelle sind effektive Beschreibungen einer mikroskopischen Theorie, die zusätzliche Neuronen hat und nur Zwei-Körper-Wechselwirkungen zwischen ihnen erfordert. Aus diesem Grund ist diese mikroskopische Theorie ein gültiges Modell eines großen assoziativen Gedächtnisses mit einem gewissen Grad an biologischer Plausibilität. Die Dynamik des Netzwerks und sein reduziertes dimensionales Äquivalent minimieren beide Energiefunktionen (Lyapunov-Funktionen).

### Arbeitsweise

In diesem Modell wird eine Menge von Komplexneuronen an eine Menge von Featureneuronen gekoppelt. Wenn die synaptischen Kopplungen und Neuronaktivierungsfunktionen angemessen ausgewählt werden, hat dieses dynamische System eine Energiefunktion, die seine Dynamik beschreibt. Die Minima (stabilen Punkte) dieser Dynamik befinden sich an denselben Stellen im Unterraum wie die Minima im entsprechenden dichten assoziativen Speichersystem. Wichtig ist, dass das resultierende dynamische System eine mathematische Struktur eines herkömmlichen wiederkehrenden neuronalen Netzes aufweist, in dem die Neuronen nur paarweise durch eine Matrix synaptischer Verbindungen interagieren.
Die Nervenimpulse von Aktionspotentialen in einer präsynaptischen Zelle erzeugen Eingangsströme in ein postsynaptisches Neuron. Als Folge eines einzelnen Nervenimpulses in der präsynaptischen Zelle steigt der Strom im postsynaptischen Neuron augenblicklich an und fällt dann exponentiell mit einer Zeitkonstante 
$\tau $

 ab. Im Folgenden werden die Ströme der Featureneuronen mit 
$v_{i}$

 bezeichnet, und die Ströme der Komplexneuronen werden mit 
$h_{\mu }$

 bezeichnet. Es gibt keine synaptischen Verbindungen innerhalb der Featureneuronen oder innerhalb der Komplexneuronen. Eine Matrix 
$\xi _{\mu i}$

 bezeichnet die Stärke von Synapsen von einem Featureneuron 
$i$

 zu dem Komplexneuron 
$\mu $

. Alle Synapsen werden als symmetrisch angenommen, so dass 
$\xi _{i\mu }=\xi _{\mu i}$

 für alle Featureneuronen 
$i$

 und alle Komplexneuronen 
$\mu $

 ist. Die Ausgabefunktionen der Komplexneuronen und der Featureneuronen werden mit 
$f_{\mu }$

 und 
$g_{i}$

 bezeichnet, die nichtlineare Funktionen der entsprechenden Ströme sind. Die Funktionen 
$f(h_{\mu })$

 und 
$g(v_{i})$

 sind die einzigen Nichtlinearitäten, die in diesem Modell auftreten. Schließlich werden die Zeitkonstanten für die beiden Gruppen von Neuronen mit 
$\tau _{f}$

 und 
$\tau _{h}$

 bezeichnet. Das Modell kann mit folgenden Gleichungen beschrieben werden:

${\begin{aligned}\tau _{f}{\frac {dv_{i}}{dt}}&=\sum _{\mu =1}^{N_{h}}\xi _{i\mu }f_{\mu }-v_{i}+I_{i}\\\tau _{h}{\frac {dh_{\mu }}{dt}}&=\sum _{i=1}^{N_{f}}\xi _{\mu i}g_{i}-h_{\mu }\end{aligned}}$

Mathematisch beschreiben Gleichungen die zeitliche Entwicklung von zwei Gruppen von Neuronen. Für jedes Neuron werden seine zeitlichen Aktualisierungen durch die Eingaben von anderen Neuronen und seinem eigenen Zustand bestimmt. Aus diesem Grund wird die Energiefunktion für dieses System als Summe von drei Termen dargestellt: zwei Terme, die die Neuronen in jeder spezifischen Gruppe beschreiben, und der Interaktionsterm zwischen den beiden Gruppen von Neuronen. Mit diesen Auswahlmöglichkeiten kann die Energiefunktion für das Netzwerk geschrieben werden als

$E(t)=\left(\sum _{i=1}^{N_{f}}(v_{i}-I_{i})g_{i}-L_{x}\right)+\left(\sum _{\mu =1}^{N_{h}}h_{\mu }f_{\mu }-L_{h}\right)-\sum _{\mu ,i}f_{\mu }\xi _{\mu i}g_{i}$

Durch Zeitableitung der Energie und Verwendung dynamischer Gleichungen kann gezeigt werden, dass die Energie auf der dynamischen Trajektorie monoton abnimmt:

${\frac {dE(t)}{dt}}=-\tau _{f}\sum \limits _{i,j=1}^{N_{f}}{\frac {dv_{i}}{dt}}{\frac {\partial ^{2}L_{v}}{\partial v_{i}\partial v_{j}}}{\frac {dx_{j}}{dt}}-\tau _{h}\sum \limits _{\mu ,\nu =1}^{N_{h}}{\frac {dh_{\mu }}{dt}}{\frac {\partial ^{2}L_{h}}{\partial h_{\mu }\partial h_{\nu }}}{\frac {dh_{\nu }}{dt}}\leq 0$

Die letzte Ungleichung gilt, wenn die Hesse-Matrizen der Lagrange-Funktionen positiv semidefinit sind. Neben der Abnahme der Energiefunktion auf der dynamischen Bahn ist es wichtig zu prüfen, ob bei einer bestimmten Wahl der Aktivierungsfunktionen oder Lagrange-Funktionen die entsprechende Energie nach unten begrenzt wird. Dies kann beispielsweise erreicht werden, indem eine beschränkte Aktivierungsfunktion für die Featureneuronen 
$g(v_{i})$

 verwendet wird, z. B. hyperbolischer Tangens oder eine Sigmoidfunktion. Vorausgesetzt, dass die Energie begrenzt ist, wird die Dynamik des neuronalen Netzwerks schließlich einen festen Punkt erreichen, der einem der lokalen Minima der Energiefunktion entspricht. Die Energiefunktion enthält drei Terme: Der erste Term hängt nur von den Featureneuronen ab, der zweite Term hängt nur von den Komplexneuronen ab und der dritte Term ist der Interaktionsterm zwischen den beiden Gruppen von Neuronen.
Jehoshua Bruck bewies im Jahr 1990 die Konvergenz von diskreten Hopfield-Netzwerken. In einer späteren Arbeit wurde das Verhalten jedes Neurons sowohl in zeitdiskreten als auch in zeitkontinuierlichen Hopfield-Netzwerken weiter untersucht. Bruck bewies, dass das Neuron 
$j$

 seinen Zustand genau dann ändert, wenn es den folgenden Pseudo-Cut weiter verringert. Das diskrete Hopfield-Netzwerk minimiert den folgenden Pseudo-Cut für die synaptische Gewichtsmatrix des Hopfield-Netzwerks.

$J_{pseudo-cut}(k)=\sum _{i\in C_{1}(k)}\sum _{j\in C_{2}(k)}w_{ij}+\sum _{j\in C_{1}(k)}{\theta _{j}}$

wobei 
$C_{1}(k)$

 und 
$C_{2}(k)$

 die Menge der Neuronen darstellen, die zum Zeitpunkt k gleich −1 bzw. +1 sind. Das zeitdiskrete Hopfield-Netzwerk minimiert immer genau den folgenden Pseudo-Cut.

$U(k)=\sum _{i=1}^{N}\sum _{j=1}^{N}w_{ij}(s_{i}(k)-s_{j}(k))^{2}+2\sum _{j=1}^{N}\theta _{j}s_{j}(k)$

Das zeitkontinuierliche Hopfield-Netzwerk minimiert immer eine Obergrenze für den folgenden gewichteten Schnitt, wobei 
$f$

 eine nullzentrierte Sigmoidfunktion ist.

$V(t)=\sum _{i=1}^{N}\sum _{j=1}^{N}w_{ij}(f(s_{i}(t))-f(s_{j}(t))^{2}+2\sum _{j=1}^{N}\theta _{j}f(s_{j}(t))$

## Moderne Hopfield-Netze

Moderne Hopfield-Netze zeichnen sich durch die Fähigkeit aus, mit einer großen Anzahl von Mustern effizient umzugehen, indem sie kontinuierliche Aktivierungen und fortgeschrittene Optimierungsansätze nutzen, was ihre Speicher- und Mustererkennungsleistung erheblich verbessert.
Biologische neuronale Netze weisen eine große Heterogenität hinsichtlich unterschiedlicher Zelltypen auf. Das folgende mathematische Modell beschreibt ein vollständig verbundenes assoziatives Speichernetzwerk unter Annahme des extremen Grades an Heterogenität: Es wird angenommen, dass das Netzwerk vollständig verbunden ist, sodass jedes Neuron mit jedem anderen Neuron unter Verwendung einer symmetrischen Matrix von Gewichten 
$W_{IJ}$

 verbunden ist, wobei die Indexe 
$I$

 und 
$J$

 verschiedene Neuronen im Netzwerk bezeichnen. Der einfachste Weg, dieses Problem mathematisch zu formulieren, besteht darin, das Netzwerk durch eine Lagrange-Funktion 
$L(\{x_{I}\})$

 zu definieren, die von den Aktivitäten aller Neuronen im Netzwerk abhängt. Die Aktivierungsfunktion für jedes Neuron ist als partielle Ableitung der Lagrange-Funktion in Bezug auf die Aktivität dieses Neurons definiert:

$g_{I}={\frac {\partial L}{\partial x_{I}}}$

Man kann sich 
$g_{I}$

 als axonalen Ausgang des Neurons 
$I$

 vorstellen. Im einfachsten Fall, wenn die Lagrange-Funktion für verschiedene Neuronen additiv ist, führt diese Definition zu einer Aktivierung, die eine nichtlineare Funktion der Aktivität dieses Neurons ist. Bei nicht-additiven Lagrange-Funktionen kann diese Aktivierungsfunktion von den Aktivitäten einer Gruppe von Neuronen abhängen. Die dynamischen Gleichungen, die die zeitliche Entwicklung eines gegebenen Neurons 
$I$

 beschreiben, sind gegeben durch

$\tau _{f}{\frac {dx_{I}}{dt}}=\sum _{J=1}^{N}W_{IJ}g_{J}-x_{I}$

Jedes Neuron 
$I$

 sammelt die axonalen Ausgabewerte 
$g_{J}$

 aller Neuronen, gewichtet sie mit den synaptischen Koeffizienten 
$W_{IJ}$

 und erzeugt seine eigene zeitabhängige Aktivität 
$x_{I}$

. Die zeitliche Entwicklung hat eine Zeitkonstante 
$\tau _{I}$

, die im Allgemeinen für jedes Neuron unterschiedlich sein kann. Dieses Netzwerk hat eine globale Energiefunktion

$E=\sum _{I=1}^{N}x_{I}g_{I}-L-{\frac {1}{2}}\sum _{I,J=1}^{N}g_{I}W_{IJ}g_{J}$

## Beziehung zur statistischen Mechanik

Die Dynamik der Neuronenaktualisierung (Hopfield-Netzen) ist analog zur Energie-Minimierung in physikalischen Systemen (statistischen Mechanik), wobei das Netzwerk einem niedrigeren Energiezustand (Attraktor) zustrebt, ähnlich wie Teilchen in einem System thermodynamischen Gleichgewichts erreichen.
Für das Hopfield-Modell existiert eine Energiefunktion der Form

$E=-{\frac {1}{2}}\sum _{i\neq j}{w_{ij}{s_{i}}{s_{j}}}+\sum _{i}{\theta _{i}s_{i}}$

,
deren Wert, wie sich beweisen lässt, bei jeder Aktualisierung gemäß obiger Regel abnimmt. Nur bei den stabilen Mustern (und den unechten Zuständen) bleibt auch die Energie gleich, diese stellen also lokale Minima der Energielandschaft dar.
Es gibt einen Zusammenhang zwischen dem Hopfield-Modell und dem Ising-Modell, für dessen Energie gilt:

$E=-{\frac {1}{2}}\sum _{\langle ij\rangle }{J_{ij}{s_{i}}{s_{j}}}+\sum _{i}{h_{i}s_{i}}$

.
Insbesondere zu Spingläsern, bei denen die 
$J_{ij}$

 zufällig verteilt sind, besteht große Ähnlichkeit. So konnte mit Methoden der theoretischen Physik gezeigt werden, dass Hopfieldnetze nur bis zu einem Verhältnis 
${\tfrac {L}{N}}=0{,}138$

 als assoziatives Gedächtnis verwendbar sind.

## Konvergenzsatz

Der Konvergenzsatz in Bezug auf Hopfield-Netze beschreibt die mathematische Eigenschaft, dass das Netzwerk nach einer endlichen Anzahl von Aktualisierungen der Neuronen in einen stabilen Zustand übergeht, der einem der gespeicherten Muster entspricht.
Der Konvergenzsatz für Hopfield-Netze lautet: Werden die Aktivierungen der Neuronen eines Hopfield-Netzes sequentiell aktualisiert, so wird in endlich vielen Schritten ein stabiler Zustand erreicht. Werden die Neuronen in beliebiger, aber fester Reihenfolge zyklisch durchlaufen, sind höchstens 
$n\cdot 2^{n}$

 Schritte für Updates einzelner Neuronen nötig, wobei 
$n$

 die Anzahl der Neuronen des Hopfield-Netzes ist.
Vorausgesetzt, die Neuronen werden in einer beliebigen, aber festen Reihenfolge aktualisiert, garantiert dies, dass die Neuronen zyklisch durchlaufen werden, und daher jedes Neuron alle 
$n$

 Schritte aktualisiert wird. Ändert sich beim Durchlaufen aller 
$n$

 Neuronen keine Aktivierung, ist ein stabiler Zustand erreicht. Ändert sich beim Durchlaufen aller 
$n$

 Neuronen mindestens eine Aktivierung, kann der vorherige Zustand nicht wieder erreicht werden, weil entweder der neue Zustand eine geringere Energie hat als der alte (denn Updates können die Netzenergie nicht erhöhen) oder die Anzahl der Aktivierungen hat zugenommen (denn gleiche Energie ist nur für 
$n$

 möglich). Die Anzahl möglicher Zustände des Hopfield-Netzes ist 
$2^{n}$

, von denen mindestens einer bei jedem Durchlauf der 
$n$

 Neuronen unerreichbar gemacht werden muss.
