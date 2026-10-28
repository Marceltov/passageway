---
title: Bestärkendes Lernen
url: https://de.wikipedia.org/wiki/Best%C3%A4rkendes_Lernen
updated: '2026-07-07T10:21:10Z'
language: de
revision: '268577713'
license: CC BY-SA 4.0
source: Wikipedia
---

Bestärkendes Lernen oder verstärkendes Lernen (englisch reinforcement learning, RL) steht für einen Lernstil des maschinellen Lernens. Dabei führt ein KI-Agent selbständig Aktionen in einer dynamischen Umgebung aus und erlernt durch Versuch und Irrtum eine Strategie (englisch policy), die die Summe der erhaltenen Belohnungen (englisch rewards) maximiert.

## Beschreibung

Der Begriff ist der Psychologie entlehnt und wurde bereits seit den Anfängen der Kybernetik verwendet. So benutzte schon Marvin Minsky den Begriff in seiner Dissertation von 1954. Die Modelle des bestärkenden Lernens versuchen, das Lernverhalten in der Natur nachzubilden.
Die Umgebung wird in der Regel als Markov-Entscheidungsproblem (MDP) beschrieben. Eine klassische Methode für das Lösen eines MDPs ist die dynamische Programmierung. Dazu muss ein genaues mathematisches Modell für das Problem bekannt sein. Außerdem ist die Zahl der Zustände, die effizient verarbeitet werden können, begrenzt. Der wesentliche Unterschied zwischen klassischen Methoden und denen des bestärkenden Lernens besteht darin, dass die Methoden des bestärkenden Lernens kein Modell für das Markov-Entscheidungsproblem voraussetzen und sie auch auf MDPs mit vielen Zuständen effizient angewendet werden können.
Diese Methoden müssen einen Kompromiss finden zwischen dem Erkunden (englisch exploration) von noch unbekannten Zuständen und dem Ausnutzen (englisch exploitation) von erlerntem Wissen, mit dem der Agent die Summe der erhaltenen Belohnungen maximiert. Dabei können Belohnungen auch verzögert eintreffen. Eine Aktion, auf die zunächst keine hohe Belohnung erfolgt, kann zu einem Zustand führen, von dem aus mit weiteren Aktionen eine hohe Belohnung erreicht werden kann.
Beim bestärkenden Lernen wird die Theorie der optimalen Steuerung angewendet. Ein einfacher Ansatz ist das Q-Lernen. Dabei werden Erfahrungswerte zu Zuständen und Aktionen direkt in Tabellen gespeichert. Es wird kein Modell von der Umgebung erstellt. Q-Lernen funktioniert gut bei Problemstellungen, die nur wenige Zustände und Aktionen enthalten, so dass der Agent beim Lernen mit Sicherheit jeden Zustand mehrfach erreichen und darin Aktionen ausführen kann. Andere Ansätze erstellen beim Lernen ein Modell der Umgebung.
Ein Spezialfall ist die Verwendung eines Bewertungsmodells, welches durch menschliche Interaktion mit überwachtem Lernen vorprogrammiert wird und die Interaktion mit der Umgebung ergänzt. In diesem Fall erfolgt bestärkendes Lernen durch menschlich beeinflusste Rückkopplung (englisch reinforcement learning through human feedback, (RLHF)).

## Grundlagen

Die mathematischen Grundlagen des bestärkenden Lernens bilden die folgenden fünf Begriffe: Der Agent (englisch agent), die Umwelt (englisch environment), die Zustände (englisch states), die Aktionen (englisch actions) und die Belohnungen (englisch rewards). Die Methoden des bestärkenden Lernens betrachten die Interaktion des lernenden Agenten mit seiner Umgebung. Einfache Beispiele sind ein Saugroboter, dessen Belohnung in der Staubmenge besteht, die er in einer bestimmten Zeit aufsaugt oder ein beweglicher Roboter, der in einem Labyrinth steht und mit möglichst wenigen Schritten zu einem bestimmten Feld gehen soll.

### Beschreibung der Umgebung

Die Umgebung wird in der Regel als Markow-Entscheidungsproblem (englisch markov decision process, MDP) formuliert. Die Interaktion des Agenten mit der Umgebung findet zu diskreten Zeitpunkten 
$t\in \mathbb {N} _{0}$

 statt. Zu jedem Zeitpunkt befindet sich der Agent in einem Zustand, wählt eine Aktion aus und erhält dafür eine reellwertige Belohnung.
Das Markow-Entscheidungsproblem ist ein Tupel 
$(S,A,T,r,p_{0})$

, wobei

$S$

 eine Menge von Zuständen,

$A$

 eine Menge von Aktionen,

$T$

 das Aktionsmodell (auch Transitionswahrscheinlichkeit) 
$T\colon S\times A\times S\rightarrow [0,1]$

 ist, so dass 
$T(s_{t},a_{t},s_{t+1})=p(s_{t+1}|s_{t},a_{t})$

 die Wahrscheinlichkeit ist, von Zustand 
$s_{t}$

 durch Ausführen von Aktion 
$a_{t}$

 in den Zustand 
$s_{t+1}$

 zu gelangen.

$r\colon S\times A\times S\rightarrow \mathbb {R} $

 die Belohnungsfunktion ist, die allen Zustandsübergängen eine Belohnung zuordnet und

$p_{0}\colon S\rightarrow \mathbb {R} $

 die Startverteilung ist, die zu jedem Zustand angibt, wie wahrscheinlich es ist, in diesem Zustand zu starten.
Eine Policy 
$\pi $

 ist eine Kollektion von Wahrscheinlichkeitsmaßen 
$(\pi _{t}(\cdot \mid s))_{s\in {\mathcal {S}}}$

 auf 
${\mathcal {A}}$

. 
$\pi _{t}(a\mid s)$

 gibt dabei die Präferenz des Agenten an, zum Zeitpunkt 
$t$

 die Aktion 
$a$

 zu wählen, wenn er sich in Zustand 
$s$

 befindet. In Zufallsvariablen gesprochen bedeutet dies 
$A_{t}\sim \pi _{t}(\cdot \mid S_{t})$

.

### Total Discounted Reward Kriterium

Man kann die Qualität einer Policy 
$\pi $

 bestimmen, indem man den Gewinn, den man mit ihr erzielt, mit dem Gewinn vergleicht, den man mit einer optimalen Policy 
$\pi ^{*}$

 erzielen kann. Um annähernd optimal zu handeln, muss der Agent die langfristigen Folgen seiner Handlungen berücksichtigen, auch wenn die damit verbundene unmittelbare Belohnung negativ sein könnte.
Ziel des Agenten ist es, den insgesamt erwarteten Gewinn (englisch total discounted reward) zu maximieren. Dieser Gewinn wird auch kumulierter Reward genannt. Er wird in der Regel als Summe aller Belohnungen 
$r$

 über unendlich viele Zustandsübergänge berechnet:

$\mathbb {E} [G_{t}]=\mathbb {E} \left[\sum _{i=0}^{\infty }\gamma ^{i}\cdot r_{t+i}\right]$

 mit 
$0\leq \gamma <1$

Dabei ist 
$r_{t+i}$

 die Belohnung, die der Agent wahrscheinlich im Zeitschritt 
$t+1$

 erhält. Der Diskontierungsfaktor 
$\gamma $

 gewichtet Belohnungen, die kurzfristig erfolgen, höher als solche, die später erfolgen. Er sorgt auch dafür, dass die Summe für kontinuierliche Probleme (unendlich viele Zustandsübergänge) gegen einen Grenzwert konvergiert. Für 
$\gamma =0$

 zählt nur die direkte Belohnung einer Aktion, alle zukünftigen Belohnungen werden ignoriert. Für 
$\gamma \rightarrow 1$

 erhalten zukünftige Belohnungen immer mehr Gewicht. Typische Werte für 
$\gamma $

 liegen zwischen 0,95 und 0,99.

### Erkundung der Umgebung

Wenn alle Elemente eines MDP vollständig bekannt sind und er nicht zu viele Zustände enthält, kann die optimale Policy direkt mit dynamischer Programmierung berechnet werden, siehe auch Markow-Entscheidungsproblem#Algorithmen. Bei vielen Aufgaben, die mit bestärkendem Lernen gelöst werden sollen, ist das Aktionsmodell 
$T$

 nicht bekannt. Bei diesen Aufgaben spielt die autonome Erkundung der Umgebung eine wichtige Rolle. Der Agent kann selbstständig eine Erkundungs-Policy ausführen, um durch Versuch und Irrtum entweder das Aktionsmodell oder, statt einem Modell, direkt eine optimale Policy zu erlernen. In einigen Aufgabenstellungen kann der Agent allerdings nur einen Teil der Zustände beobachten oder die Beobachtungen können ungenau sein. Formal muss das Problem dann als teilweise beobachtbares Markow-Entscheidungsproblem (englisch partially observable Markov decision process, (POMDP)) beschrieben werden. In beiden Fällen kann es auch Einschränkungen geben für die Aktionen, die der Agent ausführen kann.
Zur Erkundung ist ein rein zufälliges Vorgehen nicht effizient. Der Agent sollte sinnvolle Ansätze verfolgen und dabei bereits erworbenes Wissen ausnutzen (englisch exploitation). Er soll sich aber nicht zu früh festlegen und weiter nach neuen, noch besseren Aktionsmöglichkeiten suchen (englisch exploration). Eine prominente Erkundungs-Policy ist die ε-greedy policy. Hierbei ist der Agent entweder gierig (englisch greedy) und wählt die aus seiner Sicht erfolgversprechendste Aktion (gemäß seinem bereits erworbenen Wissen) oder er wählt eine zufällige Aktion. Der Parameter ε mit Werten zwischen 0 und 1 gibt die Wahrscheinlichkeit an, mit der er eine zufällige Aktion wählt.

### Wesentliche Fähigkeiten

Der Erfolg von bestärkendem Lernen beim Lösen von Aufgaben in komplexen Umgebungen beruht im Wesentlichen auf zwei Fähigkeiten. Erstens kann der Agent seine Umwelt erforschen und mit Hilfe der Rückmeldungen seine Policy verbessern. Zweitens kann er in Umgebungen, in denen eine direkte Berechnung der optimalen Policy nicht effizient möglich ist, die zugehörige Funktion approximieren. Dadurch eignet sich das bestärkende Lernen insbesondere für das Lösen von Aufgaben, bei denen:

Die einzige Möglichkeit, die nötigen Informationen zu erhalten, darin besteht, die Umwelt aktiv zu erforschen;
Das Modell der Umgebung vollständig bekannt ist, es aber zu umfangreich ist, um eine analytische Lösung zu berechnen.
Das erste Problem ist ein „echtes“ Lernproblem. Das zweite Problem ist eigentlich ein Planungsproblem, denn das Modell der Umwelt ist vorab bekannt.

## Lernverfahren

Zum Erlernen der Strategie des Agenten gibt es verschiedene Algorithmen. Sie lassen sich grob einteilen in modellbasiert und modellfrei. Modellbasierte Methoden lernen das Aktionsmodell 
$T$

 und die Belohnungsfunktion 
$r$

 und berechnen daraus die optimale Strategie. Modellfreie Methoden lernen für jeden Zustand die optimale Aktion. Der Agent kennt nur die optimalen Aktionen. Er kann nicht vorhersagen, zu welchen Folgezuständen die Aktionen führen.

### Modellfrei

Die am häufigsten genutzten modellfreien Ansätze sind wertbasiert oder strategiebasiert. Die Mischform wird meist als Actor-Critic bezeichnet.

#### Wertbasiert

Wertbasierte Methoden bestimmen für jeden Zustand und jede Aktion, die darin ausgeführt werden kann, den kumulierten Reward. Dieser wird als Summe der direkten Belohnung auf die Aktion und allen zukünftig zu erwartenden Belohnungen berechnet. Der Agent lernt eine Nutzenfunktion, die den kumulierten Reward maximiert.
Bei kleinen Zustands- oder Aktionsräumen können alle Werte in einer Tabelle gespeichert werden, deren Felder anhand der erhaltenen Belohnungen aktualisiert werden. Bei großen Zustandsräumen muss die Nutzenfunktion jedoch approximiert werden. Dazu eignet sich beispielsweise die Fourierreihe oder auch ein Neuronales Netz.
Bekannte Beispiele sind Monte-Carlo-Methoden und Temporal Difference Learning.

##### Monte-Carlo-Methoden

Die Grundidee der Monte-Carlo-Methoden besteht darin, den Wert einer bestimmten Aktion in einem bestimmten Zustand dadurch abzuschätzen, dass man eine hinreichend große Menge von zufällig gewählten Episoden ausführt, die den Zustand besuchen und die Aktion ausführen und den Mittelwert der erhaltenen Belohnungen bildet. Der Mittelwert berücksichtigt für jede Episode die Summe aller Belohnungen, die nach der Aktion erhalten wurden.
Der Begriff „Monte Carlo“ steht allgemein für jede Methode, die eine Zufallsstichprobe beinhaltet. Im hier gegebenen Kontext ist das wesentliche Merkmal von Monte-Carlo-Methoden, dass sie die Aktualisierungen jeweils nach einer abgeschlossenen Episode durchführen. Sie können nur auf episodische Aufgabenstellungen angewendet werden. Sie warten das Ergebnis einer vollständigen Episode ab und aktualisieren danach die Mittelwerte für die ausgeführten Aktionen. Die Ergebnisse sind vom weiteren Verlauf der Episode abhängig. Ein ungünstiger weiterer Verlauf in einer Episode senkt das Ergebnis und damit auch den Schätzwert für eine Aktion. Deshalb können Monte-Carlo-Methoden eine suboptimale Lösung berechnen, wenn keine geeigneten Gegenmaßnahmen ergriffen werden.

##### Temporal Difference Learning

Temporal Difference Learning passt den systematischen Ansatz des Q-Wert-Iterationsalgorithmus, der die optimale Strategie für ein vollständig bekanntes Markow-Entscheidungsproblem berechnen kann, an Probleme an, bei denen das Aktionsmodell und die Belohnungfunktion nicht bekannt sind. Die Methoden erkunden die Umgebung und verwenden in jedem Schritt direkt die Belohnung, die die Umgebung zur ausgeführten Aktion zurückmeldet. Dabei kombinieren sie die direkte Belohnung mit Schätzungen zum optimalen zukünftigen Verlauf. Den so erhaltenen Wert verwenden sie, um die Schätzung für den Wert der Aktion zu aktualisieren. Gegenüber Monte-Carlo-Methoden hat dieses Vorgehen entscheidende Vorteile: Die Schätzung ist unabhängig vom weiteren Verlauf der Episode, sie benötigt weniger Zeit und sie ist auch bei Aufgabenstellungen möglich, die unendlich weitergeführt werden können. Außerdem wurde die Konvergenz zur optimalen Wertfunktion bewiesen. Eine sehr verbreitete Variante ist Q-Lernen.
Sollen mehrere Agenten kooperieren und mit Q-Lernen eine optimale Strategie dafür lernen, kann (bislang) nur in trivialen Fällen die Konvergenz der Lernvorgänge garantiert werden. Trotzdem kann unter Zuhilfenahme von Heuristiken oft ein in der Praxis nützliches Verhalten gelernt werden, da der worst case selten auftritt.

#### Strategiebasiert

Strategiebasierte Methoden versuchen, die zu erwartende kumulative Belohnung direkt durch Parametrisierung der Strategie zu maximieren. Meistens erfolgt diese Maximierung durch stochastisch gradientbasierte Optimierung (englisch policy gradient). Prominente Vertreter dieser Klasse sind REINFORCE, Trust Region Policy Optimization (TRPO) und Proximal Policy Optimization (PPO).

#### Beispiel REINFORCE

Der einfach herzuleitende Algorithmus REINFORCE schätzt den Gradienten des zu erwartenden Gewinnes

$\nabla _{\theta }\mathbf {E} _{\tau \sim p_{\theta }}[R_{0}]$

, um damit seine Parameter über empirisch gewinnbare Spielabläufe zu aktualisieren. Hierbei muss die Strategie 
$\pi _{\theta }(a|s)$

 nach 
$\theta $

 differenzierbar sein und 
$\tau =(s_{0},a_{0},s_{1},a_{1},\dots ,s_{T},a_{T})$

 stellt einen Spielablauf dar, der aus der Wahrscheinlichkeitsverteilung 
$p_{\theta }$

 entnommen wird. Diese setzt sich einerseits aus der Strategie 
$\pi _{\theta }$

, als auch der möglicherweise nicht-deterministischen Umgebung 
$p(s'|s,a)$

 (auf die der Agent keinen Einfluss hat), zusammen:

$p_{\theta }(\tau )=\mu (s_{0})\prod _{t=0}^{T}p(s_{t+1}|s_{t},a_{t})\;\pi _{\theta }(a_{t}|s_{t})$

,
wobei 
$\mu $

 eine Verteilung über den Startzustand darstellt. Über die Definition der Erwartungswerts kann nun REINFORCE wie folgt hergeleitet werden:

$\nabla _{\theta }\mathbf {E} _{\tau \sim p_{\theta }}[R_{0}]=\nabla _{\theta }\int R_{0}\;p_{\theta }(\tau )d\tau =\int R_{0}\;\nabla _{\theta }p_{\theta }(\tau )d\tau =$

:
$\int R_{0}\;\nabla _{\theta }{\text{log}}(p_{\theta }(\tau ))p_{\theta }(\tau )d\tau =\mathbf {E} _{\tau \sim p_{\theta }}[R_{0}\nabla _{\theta }{\text{log}}(p_{\theta }(\tau ))],$

wobei für die erste Gleichung die Leibnizregel verwendet wurde und für die dritte Gleichung die Regel

$\nabla _{x}{\text{log}}(f(x))={\frac {\nabla _{x}f(x)}{f(x)}}$

,
wobei der natürliche Logarithmus gemeint ist. Als letzten Schritt erkennen wir, dass

$\nabla _{\theta }{\text{log}}(p_{\theta }(\tau ))=\nabla _{\theta }{\Big [}{\text{log}}(\mu (s_{0}))+\sum _{t=0}^{T}{\text{log}}(p(s_{t+1}|s_{t},a_{t}))+{\text{log}}(\pi _{\theta }(s_{t}|a_{t})){\Big ]}=\sum _{t=0}^{T}\nabla _{\theta }{\text{log}}(\pi _{\theta }(s_{t}|a_{t}))$

.
Nun kann man einen erwartungstreuen Schätzer 
${\hat {\nabla }}_{\theta }\mathbf {E} _{\tau \sim p_{\theta }}[R_{0}]$

 des Gradienten des zu erwartenden Gewinns erhalten, indem man erst einen Spielablauf 
$\tau $

 mit dem Agenten generiert und einsetzt:

${\hat {\nabla }}_{\theta }\mathbf {E} _{\tau \sim p_{\theta }}[R_{0}]=R_{0}\cdot \sum _{t=0}^{T}\nabla _{\theta }{\text{log}}(\pi _{\theta }(a_{t}|s_{t}))$

.
Der Parameterupdate mit Lernrate 
$\eta $

 erfolgt dann wie folgt:

$\theta _{t+1}\leftarrow \theta _{t}+\eta {\hat {\nabla }}_{\theta }\mathbf {E} _{\tau \sim p_{\theta }}[R_{0}]$

.

### Modellbasiert

Modellbasierte Verfahren konstruieren ein prädiktives Modell ihrer Umwelt. Dies bedeutet, dass der Agent Vorhersagen für Anfragen der Art „Was wird passieren, wenn ich eine bestimmte Aktion ausführe?“ generieren kann. Das Modell stellt somit einen (gelernten oder bekannten) reversiblen Zugang zur Umgebungsdynamik dar, da der Agent eine Vorhersage zu jedem beliebigen Zustands-Aktions-Paar ermitteln kann und nicht an die durch den Spielablauf vorgegebene Ordnung gebunden ist. Anders als in modellfreien Ansätzen ermöglicht das Modell explizites Planen. Dies wird in Algorithmen wie z. B. MuZero von Deepmind genutzt, um ein präzise Vorausberechnung zu ermöglichen, die in einigen Spielen wie Schach oder Go von besonderer Relevanz ist. Eine andere Klasse von Methoden, welche auf dem Dyna-Algorithmus
basiert, kombiniert den modellbasierten mit dem modellfreien Ansatz, indem sie das gelernte Modell nutzt, um künstliche (halluzinierte) Daten zu generieren. Diese werden dann wiederum zum Lernen einer Strategie und/oder Wertfunktion eingesetzt.
Forschende erhoffen sich, dass modellbasierte RL-Methoden künftig noch mehr zum Verständnis realer Kausalitäten medizinischer, sozial- und wirtschaftswissenschaftlicher Wissenschaftszweige oder Politikgestaltung beitragen können (causal machine learning), deren Themenfelder bisher über wenige inhaltliche und personelle Überschneidungen verfügen.
