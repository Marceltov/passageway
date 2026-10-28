---
title: Backpropagation
url: https://de.wikipedia.org/wiki/Backpropagation
updated: '2026-03-11T19:07:49Z'
language: de
revision: '265138298'
license: CC BY-SA 4.0
source: Wikipedia
---

Backpropagation oder auch Backpropagation of Error bzw. Fehlerrückführung bzw. Rückpropagierung ist ein verbreitetes Verfahren zum Einlernen künstlicher neuronaler Netze. Es gehört in der einfachen Form zur Gruppe der überwachten Lernverfahren und wird als Verallgemeinerung der Delta-Regel auf mehrschichtige Netze angewandt.
Die Rückwärtspropagierung ist ein Spezialfall eines allgemeinen Gradientenverfahrens in der Optimierung, basierend auf dem mittleren quadratischen Fehler.

## Funktionsweise

Ein künstliches neuronales Netz erhält Eingabedaten und bildet diese auf einen Ausgabewert ab. Die numerischen Eingabedaten werden in jeder Schicht des Netzes mit einer Matrix von Gewichten multipliziert, welche die Parameter des Netzes sind.
Beim Training des neuronalen Netzes wird die Abweichung zwischen dem Ausgabewert des Netzes und dem Zielwert des externen Lehrers (im einfachen Fall) berechnet und dieser Fehler rückwärts durch alle Schichten des Netzes propagiert (Backpropagation). Durch Backpropagation lässt sich ermitteln, welche Pfade den größten Einfluss auf den Fehler haben; sie ermöglicht es, Gewichte von Verbindungen zu stärken oder zu schwächen, um den Fehler zu verringern und eine gewünschte Vorhersage zu erreichen.
Im weiterentwickelten Fall (etwa bei der Architektur von AlphaGo) kann auch der menschliche externe Lehrer fehlen und der Zielwert aus anderen Teilen der Architektur geliefert werden.

## Algorithmus

Der Backpropagation-Algorithmus läuft in folgenden Phasen:

Ein Eingabemuster wird angelegt und vorwärts durch das Netz propagiert.
Die Ausgabe des Netzes wird mit der gewünschten Ausgabe verglichen. Die Differenz der beiden Werte wird als Fehler des Netzes erachtet.
Der Fehler wird nun wieder über die Ausgabe- zur Eingabeschicht zurück propagiert. Dabei werden die Gewichtungen der Neuronenverbindungen abhängig von ihrem Einfluss auf den Fehler geändert. Dies garantiert bei einem erneuten Anlegen der Eingabe eine Annäherung an die gewünschte Ausgabe.
Der Name des Algorithmus ergibt sich aus dem Zurückpropagieren des Fehlers (engl. error back-propagation).

## Fehlerminimierung

Beim Lernproblem wird für beliebige Netze eine möglichst zuverlässige Abbildung von gegebenen Eingabe- auf gegebene Ausgabevektoren angestrebt.
Dazu wird die Qualität der Abbildung durch eine Fehlerfunktion beschrieben, die hier durch den quadratischen Fehler definiert wird:

$E={\frac {1}{2}}\sum \limits _{i=1}^{n}(t_{i}-o_{i})^{2}$

.
Dabei ist

$E$

 der Fehler

$n$

 die Anzahl der Ausgabe-Neuronen,

$t_{i}$

 die gewünschte Soll-Ausgabe oder Zielwert (target)

$o_{i}$

 die errechnete Ist-Ausgabe (output).
Der Faktor 
${\tfrac {1}{2}}$

 wird dabei lediglich zur Vereinfachung der Ableitung hinzugenommen.
Das Ziel ist nun die Minimierung der Fehlerfunktion, wobei im Allgemeinen lediglich ein lokales Minimum gefunden wird.
Das Einlernen eines künstlichen neuronalen Netzes erfolgt bei dem Backpropagation-Verfahren durch die Änderung der Gewichte, da die Ausgabe des Netzes – außer von der Aktivierungsfunktion – direkt von ihnen abhängt.

## Geschichte

Nach verschiedenen Quellen wurden die Grundlagen des Verfahrens im Kontext der Steuerungstheorie hergeleitet durch Prinzipien dynamischer Programmierung, und zwar durch Henry J. Kelley im Jahre 1960 und Arthur E. Bryson im Jahre 1961. 1962 publizierte Stuart Dreyfus eine einfachere Herleitung durch die Kettenregel. Vladimir Vapnik zitiert einen Artikel aus dem Jahre 1963 in seinem Buch über Support Vector Machines. 1969 beschrieben Bryson und Yu-Chi Ho das Verfahren als mehrstufige Optimierung dynamischer Systeme.
Seppo Linnainmaa publizierte im Jahre 1970 schließlich die allgemeine Methode für automatisches Differenzieren (AD) diskreter Netzwerke verschachtelter differenzierbarer Funktionen. Dies ist die moderne Variante des Backpropagation-Verfahrens, welche auch bei dünner Vernetzung effizient ist.
1973 verwendete Stuart Dreyfus Backpropagation, um Parameter von Steuersystemen proportional zu ihren Fehlergradienten zu adjustieren. Paul Werbos erwähnte 1974 die Möglichkeit, dieses Prinzip auf künstliche neuronale Netze anzuwenden, und im Jahre 1982 tat er dies auf die heute weit verbreitete Art und Weise. 1986 zeigten David E. Rumelhart, Geoffrey E. Hinton und Ronald J. Williams durch Experimente, dass diese Methode zu nützlichen internen Repräsentationen von Eingabedaten in tieferen Schichten neuronaler Netze führen kann, was die Grundlage von Deep Learning ist. Eric A. Wan war 1993 der erste, der einen internationalen Mustererkennungswettbewerb durch Backpropagation gewann.

## Herleitung

Die Formel des Backpropagation-Verfahrens wird durch Differenziation hergeleitet:
Für die Ausgabe eines Neurons mit zwei Eingaben 
$x_{1}$

 und 
$x_{2}$

 erhält man eine zweidimensionale Hyperebene, wobei der Fehler des Neurons abhängig von den Gewichtungen 
$w_{1},w_{2}$

 der Eingaben 
$x_{1},x_{2}$

 ist. Diese Fehleroberfläche enthält Minima, die es zu finden gilt. Dies kann nun durch das Gradientenverfahren erreicht werden, indem von einem Punkt auf der Oberfläche aus in Richtung des stärksten Abfallens der Fehlerfunktion abgestiegen wird.

### Neuronenausgabe

Für die Herleitung des Backpropagation-Verfahrens sei die Neuronenausgabe eines künstlichen Neurons kurz dargestellt.
Die Ausgabe 
$o_{j}$

 eines künstlichen Neurons 
$j$

 lässt sich definieren durch

$o_{j}=\varphi ({\mbox{net}}_{j})$

und die Netzeingabe 
${\mbox{net}}_{j}$

 durch

${\mbox{net}}_{j}=\sum \limits _{i=1}^{n}x_{i}w_{ij}.$

Dabei ist

$\varphi $

 eine differenzierbare Aktivierungsfunktion deren Ableitung nicht überall gleich null ist,

$n$

 die Anzahl der Eingaben,

$x_{i}$

 die Eingabe 
$i$

 und

$w_{ij}$

 die Gewichtung zwischen Eingabe 
$i$

 und Neuron 
$j$

.
Auf einen Schwellwert 
$\theta _{j}$

 wird hier verzichtet. Dieser wird meist durch ein immer „feuerndes“ on-Neuron realisiert und dessen Ausgabe mit dem konstanten Wert 1 belegt. Auf diese Weise entfällt eine Unbekannte.

### Ableitung der Fehlerfunktion

Die partielle Ableitung der Fehlerfunktion 
$E$

 ergibt sich durch Verwendung der Kettenregel:

${\dfrac {\partial E}{\partial w_{ij}}}={\frac {\partial E}{\partial o_{j}}}{\frac {\partial o_{j}}{\partial {\mbox{net}}_{j}}}{\frac {\partial {\mbox{net}}_{j}}{\partial w_{ij}}}$

Mit Matrizen und Vektoren lautet die Kettenregel:

${\dfrac {\partial E}{\partial W}}={\frac {\partial E}{\partial O}}{\frac {\partial O}{\partial \mathrm {Net} }}{\frac {\partial \mathrm {Net} }{\partial W}}$

Aus den einzelnen Termen kann nun die folgende Formel berechnet werden. Dabei ist die Herleitung im Gegensatz zur einfachen Delta-Regel abhängig von zwei Fällen:

Liegt das Neuron in der Ausgabeschicht, so ist es direkt an der Ausgabe beteiligt,
liegt es dagegen in einer verdeckten Schicht, so kann die Anpassung nur indirekt berechnet werden.
Konkret:

$\Delta w_{ij}=-\eta {\dfrac {\partial E}{\partial w_{ij}}}=-\eta \delta _{j}o_{i}$

mit

$\delta _{j}={\begin{cases}\varphi '({\mbox{net}}_{j})(o_{j}-t_{j})&{\mbox{falls }}j{\mbox{ Ausgabeneuron ist,}}\\\varphi '({\mbox{net}}_{j})\sum _{k}\delta _{k}w_{jk}&{\mbox{falls }}j{\mbox{ verdecktes Neuron ist.}}\end{cases}}$

Dabei ist

$\Delta w_{ij}$

 die Änderung des Gewichts 
$w_{ij}$

 der Verbindung von Neuron 
$i$

 zu Neuron 
$j$

,

$\eta $

 eine feste Lernrate, mit der die Stärke der Gewichtsänderungen bestimmt werden kann,

$\delta _{j}$

 das Fehlersignal des Neurons 
$j$

, entsprechend zu 
${\frac {\partial E}{\partial {\mbox{net}}_{j}}}$

,

$t_{j}$

 die Soll-Ausgabe des Ausgabeneurons 
$j$

,

$o_{i}$

 die Ausgabe des Neurons 
$i$

,

$o_{j}$

 die Ist-Ausgabe des Ausgabeneurons 
$j$

 und

$k$

 der Index der Neuronen des nachfolgenden Layers von Neuron 
$j$

.
Bei einem einschichtigen Netzwerk ist 
$o_{i}=x_{i}$

. Die Ausgabe 
$o_{i}$

 entspricht dann also den Eingängen des Netzwerks.

### Modifizierung der Gewichte

Die Variable 
$\delta _{j}$

 geht dabei auf die Unterscheidung der Neuronen ein: Liegt das Neuron in einer verdeckten Schicht, so wird seine Gewichtung abhängig von dem Fehler geändert, den die nachfolgenden Neuronen erzeugen, welche wiederum ihre Eingaben aus dem betrachteten Neuron beziehen.
Die Änderung der Gewichte kann nun wie folgt vorgenommen werden:

$w_{ij}^{\mbox{neu}}=w_{ij}^{\mbox{alt}}+\Delta w_{ij}$

.
Dabei ist

$w_{ij}^{\mbox{neu}}$

 der neue Wert des Gewichts,

$w_{ij}^{\mbox{alt}}$

 der alte Wert des Gewichts und

$\Delta w_{ij}$

 die oben berechnete Änderung des Gewichts (basierend auf 
$w_{ij}^{\mbox{alt}}$

)
Das Ziel der Backpropagation ist es, die Ableitung des Fehlers in Bezug auf die Gewichte im Netz zu finden. Wenn nach der Änderung eines Wertes in Bezug auf einen anderen Wert gesucht ist, ist dies eine Ableitung. Für die Berechnung repräsentiert jedes Neuron eine Funktion und jede Kante führt einen Vorgang auf dem angehängten Neuron aus. Man beginnt mit dem Fehlerneuron und bewegt sich jeweils ein Neuron zurück und nimmt die partielle Ableitung des aktuellen Neurons in Bezug auf den Neurons in der vorhergehenden Schicht. Jeder Ausdruck wird an den vorhergehenden Ausdruck gekettet, um den Gesamtwert zu berechnen. Dies ist die Kettenregel.

### Kettenregel

Die Vorhersagen sind eine lineare Funktion, gefolgt von einer Sigmoidfunktion. Das Modell und die Verlustfunktion lauten wie folgt:

${\begin{aligned}z&=w\cdot x+b\\y&=\sigma (z)\\{\mathcal {L}}&={\frac {1}{2}}\cdot (y-t)^{2}\\\end{aligned}}$

Partielle Ableitungen können auf dieselbe Weise berechnet werden, wie univariate Ableitungen berechnet würden. Man kann die Kostenfunktion in Bezug auf 
$w$

 und 
$b$

 erweitern und dann die Ableitungen mithilfe wiederholter Anwendungen der univariaten Kettenregel berechnen:

${\begin{aligned}{\frac {\partial {\mathcal {L}}}{\partial w}}&={\frac {\partial }{\partial w}}\left({\frac {1}{2}}(\sigma (w\cdot x+b)-t)^{2}\right)\\&=(\sigma (w\cdot x+b)-t)\cdot \sigma '(w\cdot x+b)\cdot x\\{\frac {\partial {\mathcal {L}}}{\partial b}}&={\frac {\partial }{\partial b}}\left({\frac {1}{2}}(\sigma (w\cdot x+b)-t)^{2}\right)\\&=(\sigma (w\cdot x+b)-t)\cdot \sigma '(w\cdot x+b)\\\end{aligned}}$

Die multivariable Kettenregel ist eine Verallgemeinerung der univariaten Kettenregel:

${\frac {d}{dt}}f(x(t),y(t))={\frac {\partial f}{\partial x}}\cdot {\frac {dx}{dt}}+{\frac {\partial f}{\partial y}}\cdot {\frac {dy}{dt}}$

Kostenfunktionen für das maschinelle Lernen basieren normalerweise auf Matrixberechnungen. Eine Theorie besagt, dass es immer einen Algorithmus zum Berechnen von Ableitungen einer Kostenfunktion gibt, der höchstens ein paar Mal so viele Operationen verwendet wie die Kostenfunktion selbst.
Dazu kann man einen Berechnungsgraphen betrachten, der mit der Berechnung eines Skalars 
$z$

 endet. Eine Zwischenberechnung erstellt eine Matrix 
$C$

 aus zwei Grundmatrixen 
$A$

 und 
$B$

. Bei der umgekehrten Differentiation berechnet man 
${\bar {C}}$

, eine Matrix derselben Größe wie 
$C$

, wobei 
${\bar {C}}_{ij}={\tfrac {\partial z}{\partial C_{ij}}}$

. Man muss dann dieses Ableitungssignal backpropagieren, um 
${\bar {A}}$

 und 
${\bar {B}}$

 zu berechnen, wobei 
${\bar {A}}_{ij}={\tfrac {\partial z}{\partial A_{ij}}}$

 und 
${\bar {B}}_{ij}={\tfrac {\partial z}{\partial B_{ij}}}$

. Die Kettenregel ergibt eine allgemeine Gleichung für die Backpropagation von Matrixableitungen:

${\bar {A}}_{ij}={\frac {\partial z}{\partial A_{ij}}}=\sum _{k,l}{\frac {\partial z}{\partial C_{kl}}}\cdot {\frac {\partial C_{kl}}{\partial A_{ij}}}=\sum _{k,l}\partial {\bar {C}}_{kl}\cdot {\frac {\partial C_{kl}}{\partial A_{ij}}}$

Es sollten jedoch nicht alle Terme in dieser Gleichung ausgewertet werden. Wenn 
$A$

 und 
$C$

 beide 
$n\times n$

-Matrixen sind, gibt es 
$n^{4}$

 Elemente 
${\tfrac {\partial C_{kl}}{\partial A_{ij}}}$

, wenn alle Kombinationen von 
$i$

, 
$j$

, 
$k$

 und 
$l$

 berücksichtigt werden. Ableitungen können dieselbe Rechenaufwand wie die Kostenfunktion haben können, aber die meisten Matrixfunktionen haben eine bessere Laufzeit als 
$O(n^{4})$

. Daher ist es normalerweise möglich, die obige Summe auszuwerten, ohne alle ihre Terme explizit zu berechnen.

### Aktivierungsfunktion

Der Backpropagation-Algorithmus sucht nach dem Minimum der Fehlerfunktion unter Verwendung des Gradientenverfahrens. Die Kombination von Gewichten, die die Fehlerfunktion minimiert, wird als Lösung des Lernproblems angesehen. Weil dieses Verfahren die Berechnung des Gradienten der Fehlerfunktion bei jedem Iterationsschritt erfordert, muss die Fehlerfunktion stetig und differenzierbar sein.
Eine der beliebtesten Aktivierungsfunktionen für Backpropagation-Netze ist die Sigmoidfunktion 
$s_{c}(x)={\frac {1}{1+e^{-cx}}}$

. Die Konstante 
$c$

 ist beliebig wählbar und ihr Kehrwert 
${\frac {1}{c}}$

 wird Temperaturparameter in stochastischen neuronalen Netzen genannt. Die Form des Sigmoids ändert sich entsprechend dem Wert von 
$c$

. Höhere Werte von 
$c$

 bringen die Form des Sigmoids näher an die der Heaviside-Funktion, und im Grenzwert 
$c\rightarrow \infty $

 konvergiert das Sigmoid zu einer Heaviside-Funktion.
Die Ableitung der Sigmoidfunktion nach 
$x$

 ist 
${\frac {\partial }{\partial x}}s_{c}(x)={\frac {c\cdot e^{-cx}}{(1+e^{-cx})^{2}}}=c\cdot s_{c}(x)\cdot (1-s_{c}(x))$

Eine Alternative zum Sigmoid ist das symmetrische Sigmoid, definiert als 
$S(x)=2\cdot s(x)-1={\frac {1-e^{-x}}{1+e^{-x}}}$

. Dies ist der Tangens hyperbolicus für das Argument 
${\frac {x}{2}}$

, also 
$\tanh \left({\frac {x}{2}}\right)$

.
Viele andere Arten von Aktivierungsfunktionen wurden vorgeschlagen und der Backpropagation-Algorithmus ist auf alle anwendbar. Eine differenzierbare Aktivierungsfunktion macht die von einem neuronalen Netz berechnete Funktion differenzierbar unter der Annahme, dass die Integralfunktion an jedem Knoten nur die Summe der Eingaben ist, weil das Netz selbst nur zusammengesetzte Funktionen berechnet.

## Erweiterungen

Die Wahl der Lernrate 
$\eta $

 ist wichtig für das Verfahren, da

ein zu hoher Wert eine starke Veränderung bewirkt, wodurch das Minimum verfehlt werden kann
ein zu kleiner Wert das Einlernen unnötig verlangsamt.
Verschiedene Optimierungen von Rückwärtspropagierung, z. B. Quickprop, zielen vor allem auf die Beschleunigung der Fehlerminimierung; andere Verbesserungen versuchen vor allem die Zuverlässigkeit zu erhöhen.

### Backpropagation mit variabler Lernrate

Um eine Oszillation des Netzes, d. h. alternierende Verbindungsgewichte zu vermeiden, existieren Verfeinerungen des Verfahrens, bei dem mit einer variablen Lernrate gearbeitet wird.

### Backpropagation mit Trägheitsterm

Durch die Verwendung eines variablen Trägheitsterms (Momentum) 
$\alpha $

 kann der Gradient und die letzte Änderung gewichtet werden, so dass die Gewichtsanpassung zusätzlich von der vorausgegangenen Änderung abhängt. Ist das Momentum 
$\alpha $

 gleich 0, so hängt die Änderung allein vom Gradienten ab, bei einem Wert von 1 lediglich von der letzten Änderung.
Ähnlich einer Kugel, die einen Berg hinunter rollt und deren aktuelle Geschwindigkeit nicht nur durch die aktuelle Steigung des Berges, sondern auch durch ihre eigene Trägheit bestimmt wird, lässt sich der Backpropagation ein Trägheitsterm hinzufügen:

$\Delta w_{ij}(t+1)=(1-\alpha )\eta \delta _{j}x_{i}+\alpha \Delta w_{ij}(t)$

Dabei ist

$\Delta w_{ij}(t+1)$

 die Änderung des Gewichts 
$w_{ij}(t+1)$

 der Verbindung von Neuron 
$i$

 zu Neuron 
$j$

 zum Zeitpunkt 
$(t+1)$

,

$\eta $

 eine Lernrate,

$\delta _{j}$

 das Fehlersignal des Neurons 
$j$

 und

$x_{i}$

 die Eingabe des Neurons 
$i$

,

$\alpha $

 der Einfluss des Trägheitsterms 
$\Delta w_{ij}(t)$

. Dieser entspricht der Gewichtsänderung zum vorherigen Zeitpunkt.
Damit hängt die aktuelle Gewichtsänderung 
$(t+1)$

 sowohl vom aktuellen Gradienten der Fehlerfunktion (Steigung des Berges, 1. Summand), als auch von der Gewichtsänderung des vorherigen Zeitpunktes ab (eigene Trägheit, 2. Summand).
Durch den Trägheitsterm werden unter anderem Probleme der Backpropagation-Regel in steilen Schluchten und flachen Plateaus vermieden. Da zum Beispiel in flachen Plateaus der Gradient der Fehlerfunktion sehr klein wird, käme es ohne Trägheitsterm unmittelbar zu einem „Abbremsen“ des Gradientenabstiegs, dieses „Abbremsen“ wird durch die Addition des Trägheitsterms verzögert, so dass ein flaches Plateau schneller überwunden werden kann.
Sobald der Fehler des Netzes minimal wird, kann das Einlernen abgeschlossen werden und das mehrschichtige Netz ist nun bereit, die erlernten Muster zu klassifizieren.

### Gleichungen der Backpropagation

Die Gleichungen der Backpropagation lassen sie wie folgt zusammenfassen:

${\begin{aligned}\delta _{j}^{L}&={\frac {\partial E}{\partial o_{j}^{L}}}\varphi '({\mbox{net}}_{j}^{L})\\\delta _{j}^{l}&=((w^{l+1})^{T}\delta ^{j+1})\circ \varphi '({\mbox{net}}_{j}^{l})\\{\frac {\partial E}{\partial t_{j}^{L}}}&=\delta _{j}^{l}\\{\frac {\partial E}{\partial w_{ij}^{L}}}&=o_{j}^{l-1}\delta _{i}^{l}\end{aligned}}$

Diese Gleichungen bieten eine Möglichkeit, den Gradienten der Kostenfunktion zu berechnen. Daraus ergibt sich folgender Algorithmus:

Setze die Aktivierung 
$o^{1}$

 für die Eingabeschicht
Berechne 
$z^{l}=w^{l}o^{l-1}+t^{l}$

 und 
$o^{l}=\varphi ({\mbox{net}}_{j}^{l})$

 für 
$l=2,3,\ldots ,L$

Berechne den Vektor 
${\frac {\partial E}{\partial o_{j}^{L}}}\varphi '({\mbox{net}}_{j}^{L})$

Berechne den Vektor 
$\delta _{j}^{l}=((w^{l+1})^{T}\delta ^{j+1})\circ \varphi '({\mbox{net}}_{j}^{l})$

 für 
$l=L-1,L-2,\ldots ,2$

Der Gradient der Kostenfunktion ist 
${\frac {\partial E}{\partial w_{ij}^{L}}}=o_{j}^{l-1}\delta _{i}^{l}$

 und 
${\frac {\partial E}{\partial t_{j}^{L}}}=\delta _{j}^{l}$
