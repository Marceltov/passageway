---
title: Überwachtes Lernen
url: https://de.wikipedia.org/wiki/%C3%9Cberwachtes_Lernen
updated: '2026-06-30T10:29:34Z'
language: de
revision: '268352920'
license: CC BY-SA 4.0
source: Wikipedia
---

Überwachtes Lernen (englisch supervised learning) ist eine wichtige Kategorie des Maschinellen Lernens. Dabei wird ein Lernalgorithmus mit Datensätzen trainiert und validiert, die für jede Eingabe einen passenden Ausgabewert enthalten. Man bezeichnet solche Datensätze als markiert oder gelabelt. Ein Beispiel wäre ein Datensatz mit Bildern von Katzen und Hunden, dem jemand (in der Regel ein Mensch) zu jedem Bild ein Label hinzugefügt hat, das die Information enthält, ob auf dem Bild eine Katze oder ein Hund abgebildet ist. Mit dem Datensatz wird dann ein Algorithmus trainiert, der mit Hilfe der Information der Label eine Funktion erzeugt, die idealerweise auch bei neuen Bildern korrekt erkennt, ob sie einen Hund oder eine Katze zeigen. Häufige Anwendungen für das überwachte Lernen sind Klassifikation und Regression.
Die Methode richtet sich also nach vorgegebenen Antworten für die Ausgabe. Die Ergebnisse des Lernprozesses können mit den bekannten, richtigen Antworten verglichen, also „überwacht“, werden.
Liegen die Ergebnisse der Ausgabe in einer stetigen Verteilung vor, deren Ergebnisse beliebige quantitative Werte eines vorgegebenen Wertebereiches annehmen kann, spricht man meistens von einem Regressionsproblem.
Ein Beispiel für ein solches Regressionsproblem ist die Vorhersage der Preisentwicklung von Häusern auf Basis von bestimmten Variablen oder das Bestimmen des Alters einer Person aus anderen Informationen über die Person. Es geht demnach meistens um Vorhersagen.
Liegen die Ergebnisse hingegen in diskreter Form vor bzw. sind die Werte qualitativ, spricht man von einem Klassifikationsproblem. Ein Beispiel hierfür ist, zu bestimmen, ob es sich bei einer E-Mail um Spam oder keinen Spam handelt.
Der folgende Artikel beschreibt das Vorgehen beim überwachten Lernen und stellt einige Methoden zur Lösung von Regressionsproblemen respektive zur Lösung von Klassifikationsproblemen vor.

## Vorgehen

Um ein bestimmtes Problem mit überwachtem Lernen zu lösen, werden folgende Schritte durchgeführt:

Qualitätskriterien für das Zielsystem definieren.
Die Art der Trainingsbeispiele bestimmen. Das heißt, es muss zunächst bestimmt werden, mit welchen Daten das System trainiert werden soll. Bei einer Handschriftanalyse kann es sich z. B. um einzelne handschriftliche Zeichen, ganze handschriftliche Wörter oder ganze handschriftliche Zeilen handeln.
Prüfen, ob bereits legal auf geeignete Daten zugegriffen werden kann. Wenn es noch keine geeigneten Daten gibt, führt man eine Datenerhebung entsprechend der vorangegangenen Auswahl durch. Man benötigt sowohl die erklärenden Variablen als auch die erklärten Variablen (Labels). Die erhobenen Daten müssen neue Daten so gut repräsentieren, dass eine Verallgemeinerung von den erhobenen Daten auf neue Daten mit der geforderten Genauigkeit möglich ist. Die Erhebung kann von menschlichen Experten, durch Messungen und andere Methoden vollzogen werden.
Die erhobenen Daten werden aufbereitet. Die Genauigkeit der gelernten Funktion hängt stark davon ab, wie gut ein Algorithmus die korrekte Ausgabe aus den erhobenen Daten vorhersagen kann. Deshalb sollten Ausreißer und unvollständige Daten korrigiert oder entfernt werden. Danach werden die Merkmale in einen Vektor transformiert, der die Merkmale enthält, die ein Objekt beschreiben. Merkmale mit einem kontinuierlichen Wertebereich werden in der Regel auf den Wertebereich zwischen 0 und 1 normalisiert, damit der Lernalgorithmus Merkmale mit großen absoluten Werten und Merkmale mit kleinen absoluten Werten beim Lernen gleich stark gewichtet.
Auswahl der Lernalgorithmen bzw. der Modelle, die trainiert werden. Viele Modelle unterstützen die Festlegung von Hyperparametern, mit denen der Lernvorgang optimal an die gegebene Aufgabenstellung anpasst werden kann. Bei der Auswahl der Lernalgorithmen wird deshalb auch geklärt, ob eine Hyperparameteroptimierung erforderlich ist.
Festlegen des Kreuzvalidierungsverfahrens und Aufteilen des Datensatzes. Ein einfaches Verfahren, das oft eingesetzt wird, ist die Holdout-Methode. Bei der Holdout-Methode wird der Datensatz aufgeteilt in:
einen Trainingsdatensatz, mit dem das System trainiert wird
einen Testdatensatz, mit dem nach dem Training die Vorhersagequalität des Systems für unbekannte Daten überprüft wird
ein oder mehrere Validierungsdatensätze, falls eine Hyperparameteroptimierung geplant ist
Anschließend wird der Lernalgorithmus auf dem Trainingsdatensatz ausgeführt. Gegebenenfalls werden danach mit Hilfe der Validierungsdatensätze die Hyperparameter optimiert und anschließend der Lernalgorithmus mit den optimalen Hyperparametern und allen Trainings- und Validierungsdaten erneut trainiert.
Danach wird die Genauigkeit der gelernten Funktion überprüft, beispielsweise mit dem vorher abgetrennten Testdatensatz.
Wenn das trainierte Modell die vorab definierten Qualitätskriterien erfüllt, wird es im Zielsystem integriert.

## Herausforderungen

### Zu wenige Daten für die Komplexität der „wahren Funktion“

Eine Herausforderung ist die Menge der verfügbaren Trainingsdaten in Relation zur Komplexität der „wahren Funktion“ (Klassifikator- oder Regressionsfunktion). Wenn die wahre Funktion einfach ist, dann kann ein „unflexibler“ Lernalgorithmus mit hoher Verzerrung und geringer Varianz aus einer kleinen Datenmenge lernen. Wenn die wahre Funktion jedoch sehr komplex ist (z. B. weil sie komplexe Interaktionen zwischen vielen verschiedenen Eingabemerkmalen beinhaltet und sich in verschiedenen Teilen des Eingaberaums unterschiedlich verhält), dann wird die Funktion nur aus einer sehr großen Menge von Trainingsdaten und unter Verwendung eines „flexiblen“ Lernalgorithmus mit geringer Vorspannung und hoher Varianz erlernbar sein.

### Nicht repräsentative Daten

Das Modell kann nur dann gut verallgemeinern, wenn die Trainingsdaten alle zu verallgemeinernden Fälle gut repräsentieren. Auch ein großer Datensatz kann für einzelne Fälle zu wenige Daten enthalten. Eine solche Stichprobenverzerrung hat zur Folge, dass das trainierte Modell für diese Fälle nicht gut verallgemeinern kann.

### Fehlerhafte Zielwerte

Ein weiteres mögliches Problem sind sogenannte „Ausreißer“ in den Zielwerten. Wenn einige vorgegebene Zielwerte falsch sind (aufgrund von menschlichen Fehlern oder Sensorfehlern) und der Lernalgorithmus versucht, eine Funktion zu finden, die genau zu allen Zielwerten passt, dann kommt es zu einer Überanpassung.
In der Praxis gibt es mehrere Ansätze um Probleme mit den Ausgabewerten zu verhindern, wie z. B. frühzeitiges Anhalten des Algorithmus zur Vermeidung von Überanpassung sowie das Erkennen und Entfernen der Ausreißer vor dem Training des überwachten Lernalgorithmus. Es gibt mehrere Algorithmen, die Ausreißer identifizieren und deren Entfernen ermöglichen.

### Viele nicht relevante Merkmale

Das Modell kann nur dann gut verallgemeinern, wenn die Trainingsdaten alle relevanten Merkmale enthalten und nur wenige nicht relevante Merkmale. Deshalb sollte man analysieren, welche Merkmale wirklich ausgewertet werden müssen, um das Problem zu lösen, und das Modell nur mit diesen Merkmalen trainieren.

### Auswahl eines Modells

Es steht eine breite Palette von Lernalgorithmen zur Verfügung, von denen jeder seine Stärken und Schwächen hat. Man wählt ein bestimmtes Modell aus, indem man implizit Annahmen über die Daten macht. Beispielsweise wählt man ein lineares Modell, wenn man davon ausgeht, dass die Daten linear sind und Abweichungen der Datenpunkte von einer berechneten Geraden ignoriert werden können. Für andere Daten ist vielleicht ein Binärbaum oder ein künstliches neuronales Netz besser geeignet.
Die No-free-Lunch-Theoreme besagen, dass eine bestimmte Strategie, die in einem Teilbereich besser ist als eine andere, in einem anderen Teilbereich schlechter sein muss. Um das beste Modell zu finden, ohne Annahmen über die Daten zu treffen, müsste man alle bekannten Modelle evaluieren. In der Praxis trifft man Annahmen über die Verteilung der Daten, wählt wenige Modelle aus, die dafür gut geeignet sind und evaluiert nur diese.

### Verzerrung-Varianz-Dilemma

Beim überwachten Lernen muss oft ein Kompromiss zwischen Verzerrung und Varianz gefunden werden.
Die Varianz bezieht sich auf den Betrag, um den sich die Vorhersage ändern würde, wenn das Modell sie auf der Basis eines anderen Trainingsdatensatzes treffen würde. Im Idealfall sollte die Vorhersage bei unterschiedlichen Trainingsdatensätzen nur wenig variieren. Dann kann das trainierte Modell gut verallgemeinern. Bei hoher Varianz führen jedoch unterschiedliche Trainingsdatensätze, also kleine Änderungen an den Trainingsdaten, zu sehr unterschiedlichen Vorhersagen. Dann kann das trainierte Modell nicht gut verallgemeinern. Grundsätzlich haben flexiblere statistische Methoden eine höhere Varianz, weil sie den Trainingsdatensatz sehr genau abbilden können und dadurch bei verrauschten oder wenig repräsentativen Daten das Risiko dafür steigt, dass das Modell viele Fehler macht, wenn es Vorhersagen für völlig neue Daten macht. Dieses Problem bezeichnet man als Überanpassung. Man kann eine Überanpassung dadurch reduzieren, dass man das Modell vereinfacht, indem man beispielsweise vor dem Training die erlaubten Wertebereiche für die Modellparameter einschränkt. Dieses Vorgehen nennt man Regularisierung.
Wenn das Modell andererseits zu einfach ist, dann gibt die Verzerrung den Fehler an, der dadurch entsteht, dass man das reale Problem, das sehr kompliziert sein kann, durch ein einfacheres Modell angenähert hat. Zum Beispiel geht eine lineare Regression davon aus, dass ein lineares Problem vorliegt. In der Realität liegen jedoch selten einfache lineare Probleme vor, und so führt die Durchführung einer linearen Regression oft zu einer gewissen Verzerrung zwischen der Vorhersage und dem erwarteten Ausgabewert.

## Definitionen

Um im Folgenden mathematische Zusammenhänge besser darstellen zu können, werden folgende Definitionen verwendet:

  
    
      
        
          x
          
            (
            i
            )
          
        
      
    
    {\displaystyle x^{(i)}}
  
 = Input-Variablen (auch „erklärende Variablen“ genannt)

  
    
      
        
          y
          
            (
            i
            )
          
        
      
    
    {\displaystyle y^{(i)}}
  
 = Output/Ziel-Variablen (auch „erklärte Variablen“ genannt)

  
    
      
        (
        
          x
          
            (
            i
            )
          
        
        ,
        
          y
          
            (
            i
            )
          
        
        )
      
    
    {\displaystyle (x^{(i)},y^{(i)})}
  
 = Trainingspaar/Trainingsbeispiel

  
    
      
        
          (
          
            x
            
              (
              i
              )
            
          
          ,
          
            y
            
              (
              i
              )
            
          
          )
          ;
          i
          =
          1
          ,
          …
          ,
          m
        
      
    
    {\displaystyle {(x^{(i)},y^{(i)});i=1,\ldots ,m}}
  
 = Datensatz der zum Lernen verwendet wird (auch Lerndatensatz genannt)

  
    
      
        h
        (
        x
        )
      
    
    {\displaystyle h(x)}
  
 = Die Hypothesenfunktion, die vom Algorithmus gelernt werden soll, um 
  
    
      
        y
      
    
    {\displaystyle y}
  
 möglichst genau zu approximieren

## Regressionsprobleme

Das Ziel von überwachtem Lernen im Falle von Regressionsproblemen ist meist, auf Basis von bestimmten erklärenden Variablen wie Größe oder Farbe eines Hauses etwas über diesen Sachverhalt vorauszusagen. Der Sachverhalt kann dabei grundlegend verschieden sein, beispielsweise der Preis von Häusern in bestimmter Umgebung oder die Entwicklung des Preises einer Aktie am nächsten Tag. Das Ziel ist es dementsprechend den Zusammenhang zwischen der erklärenden und der erklärten Variable anhand eines Trainingsdatensatzes zu erlernen und mit Hilfe dieses Zusammenhangs zukünftige Ereignisse, die noch nicht bekannt sind, vorherzusagen. Ein Beispiel für einen solchen Lernalgorithmus, der Vorhersagen treffen kann, ist die lineare Regression.

### Lineare Regression

Die lineare Regression ist sehr einfaches Verfahren zur Durchführung einer Regression. Das dazu verwendete Modell ist linear in den Parametern, wobei die abhängige Variable eine Funktion der unabhängigen Variablen ist. Bei der Regression sind die Ausgaben der unbekannten Funktion verrauscht (fehlerbehaftet).

  
    
      
        y
        =
        
          h
          
            θ
          
        
        (
        x
        )
        +
        ε
      
    
    {\displaystyle y=h_{\theta }(x)+\varepsilon }
  
,
wobei 
  
    
      
        
          h
          
            θ
          
        
        (
        x
        )
        ∈
        
          R
        
      
    
    {\displaystyle h_{\theta }(x)\in \mathbb {R} }
  
 die unbekannte Funktion darstellt und 
  
    
      
        ε
      
    
    {\displaystyle \varepsilon }
  
 für zufälliges Rauschen steht. Die Erklärung für das Rauschen liegt darin, dass es zusätzliche verborgene Variablen gibt, die unbeobachtbar sind. Hierzu wird die folgende Regressionsfunktion verwendet:

  
    
      
        
          h
          
            θ
          
        
        (
        x
        )
        =
        
          θ
          
            0
          
        
        +
        
          θ
          
            1
          
        
        
          x
          
            1
          
        
        +
        …
        +
        
          θ
          
            n
          
        
        
          x
          
            n
          
        
      
    
    {\displaystyle h_{\theta }(x)=\theta _{0}+\theta _{1}x_{1}+\ldots +\theta _{n}x_{n}}
  

bzw. in Vektorschreibweise:

  
    
      
        
          h
          
            θ
          
        
        (
        x
        )
        =
        
          ∑
          
            i
            =
            0
          
          
            n
          
        
        
          θ
          
            i
          
        
        
          x
          
            i
          
        
        =
        
          
            θ
          
          
            ⊤
          
        
        
          x
        
      
    
    {\displaystyle h_{\theta }(x)=\sum _{i=0}^{n}\theta _{i}x_{i}={\boldsymbol {\theta }}^{\top }\mathbf {x} }
  

Die 
  
    
      
        
          θ
          
            i
          
        
      
    
    {\displaystyle \theta _{i}}
  
 sind dabei die Parameter der Funktion und 
  
    
      
        x
      
    
    {\displaystyle x}
  
 ist der Vektor, welcher die erklärenden Variablen enthält. Dementsprechend gewichten die Parameter die einzelnen erklärenden Variablen und werden deshalb auch oft als Regressionsgewichte bezeichnet.
Um nun aus den erklärenden Variablen eine möglichst genaue Annäherung an den Output 
  
    
      
        y
      
    
    {\displaystyle y}
  
 zu erhalten, wird eine Kostenfunktion aufgestellt.
Diese Funktion beschreibt die mittlere quadratische Abweichung, die dadurch entsteht, dass die Hypothesenfunktion die zu erklärende Variable 
  
    
      
        y
      
    
    {\displaystyle y}
  
 nur approximiert und nicht genau darstellt. Die Kostenfunktion wird beispielsweise durch die folgende Gleichung beschrieben:

  
    
      
        J
        (
        θ
        )
        =
        
          
            1
            m
          
        
        
          ∑
          
            i
            =
            1
          
          
            m
          
        
        (
        
          h
          
            θ
          
        
        (
        
          x
          
            (
            i
            )
          
        
        )
        −
        
          y
          
            (
            i
            )
          
        
        
          )
          
            2
          
        
      
    
    {\displaystyle J(\theta )={\frac {1}{m}}\sum _{i=1}^{m}(h_{\theta }(x^{(i)})-y^{(i)})^{2}}
  

Das Ziel ist es nun, diese Abweichung zu minimieren. Dazu müssen die Modellparameter so gewählt werden, dass sie die jeweiligen x-Werte richtig gewichten, um dem gewünschten y-Wert möglichst nahe zu kommen.
Die optimalen Modellparameter können auf zwei verschiedene Weisen ermittelt werden.
Eine Methode ist das sogenannte Gradientenverfahren.
Diese Methode umfasst folgende Schritte:

Es werden beliebige Werte für die Parameter gewählt.
An diesem Punkt wird die Ableitung der Kostenfunktion gebildet und die steilste Steigung ermittelt
Man geht diese Steigung in die negative Richtung entlang. Dabei wird die Größe der Schritte durch eine Lernrate bestimmt.
Dieser Prozess wird so lange wiederholt bis man am Minimum der Kostenfunktion angekommen ist.
Dies ist in der folgenden Gleichung für ein einzelnes Beispiel dargestellt (Alpha steht hierbei für die Lernrate):

  
    
      
        
          θ
          
            j
          
        
        :=
        
          θ
          
            j
          
        
        +
        α
        (
        
          y
          
            (
            i
            )
          
        
        −
        
          h
          
            θ
          
        
        (
        
          x
          
            (
            i
            )
          
        
        )
        )
        
          x
          
            j
          
          
            (
            i
            )
          
        
      
    
    {\displaystyle \theta _{j}:=\theta _{j}+\alpha (y^{(i)}-h_{\theta }(x^{(i)}))x_{j}^{(i)}}
  

Diese Gleichung wird so oft wiederholt bis 
  
    
      
        y
        (
        i
        )
        −
        h
        (
        x
        )
        =
        0
      
    
    {\displaystyle y(i)-h(x)=0}
  
 bzw. bis diese Differenz minimiert wurde und der Parameter somit seinen optimalen Wert gefunden hat.
Eine weitere Methode, die verwendet werden kann, sind die sogenannten Normalgleichungen (siehe Multiple lineare Regression). Mit dieser kann die Minimierung der Kostenfunktion explizit und ohne Rückgriff auf einen iterativen Algorithmus durchgeführt werden, indem die folgende Formel implementiert wird:

  
    
      
        
          θ
        
        =
        (
        
          
            X
          
          
            ⊤
          
        
        
          X
        
        
          )
          
            −
            1
          
        
        
          
            X
          
          
            ⊤
          
        
        
          y
        
      
    
    {\displaystyle \mathbf {\theta } =(\mathbf {X} ^{\top }\mathbf {X} )^{-1}\mathbf {X} ^{\top }\mathbf {y} }
  

Diese Formel liefert uns die optimalen Werte der Parameter.
In der folgenden Tabelle sind die Vor- und Nachteile von Gradientenverfahren und der Normalgleichung dargestellt.

### Weitere Beispiele für Modelle zur Lösung von Regressionsproblemen

Polynomiale Regression
Random Forest
Künstliches neuronales Netz

## Klassifikationsprobleme

Anders als bei Regressionsproblemen kann der Output 
  
    
      
        y
      
    
    {\displaystyle y}
  
 bei Klassifikationsproblemen nur diskrete Werte annehmen, die meistens in Form von qualitativen Daten vorliegen. Beispielsweise kann die Aufgabe darin bestehen, zu bestimmen, ob es sich bei einer neuen E-Mail um Spam handelt oder nicht. Dazu wird jedem Trainingsbeispiel eine der beiden Klassen „Spam“ oder „Kein Spam“ zugeordnet. Die Trainingsdaten dann bestehen aus den erklärenden Variablen 
  
    
      
        
          x
          
            (
            i
            )
          
        
      
    
    {\displaystyle x^{(i)}}
  
 und dem Output 
  
    
      
        y
      
    
    {\displaystyle y}
  
, bei dem der Wert 
  
    
      
        1
      
    
    {\displaystyle 1}
  
 der Klasse „Spam“ entspricht und der Wert 
  
    
      
        0
      
    
    {\displaystyle 0}
  
 der Klasse „Kein Spam“.
Man unterscheidet zudem zwischen Binären Klassifikationsproblemen und Klassifikationsproblemen, bei denen multiple Klassen vorliegen. Ein Beispiel hierfür wäre zu klassifizieren von welcher von drei Marken ein gekauftes Produkt ist (Die Klassen sind in diesem Fall Marke A, B oder C).

### Logistische Regression

Die logistische Regression ist eine oft eingesetzte Methode zum Lösen von binären Klassifikationsproblemen. Sie schätzt zunächst, mit welcher Wahrscheinlichkeit ein gegebener Datenpunkt zu einer bestimmten Klasse gehört. Danach entscheidet sie, ob die berechnete Wahrscheinlichkeit größer ist als 50 %. In diesem Fall gibt sie diese Klasse als Ergebnis aus. Andernfalls gibt sie die andere Klasse als Ergebnis aus.
Die Funktion zur Schätzung der Wahrscheinlichkeiten muss Werte zwischen 0 und 1 annehmen. Die logistische Regression verwendet dazu die Sigmoidfunktion, gegeben durch folgende Gleichung:

  
    
      
        g
        (
        z
        )
        =
        
          
            
              exp
              ⁡
              (
              z
              )
            
            
              1
              +
              exp
              ⁡
              (
              z
              )
            
          
        
        =
        
          
            1
            
              1
              +
              exp
              ⁡
              (
              −
              z
              )
            
          
        
      
    
    {\displaystyle g(z)={\frac {\exp(z)}{1+\exp(z)}}={\frac {1}{1+\exp(-z)}}}
  
.
Sie lässt sich auf die Hypothesenfunktion folgendermaßen anwenden:

  
    
      
        
          h
          
            θ
          
        
        (
        x
        )
        =
        g
        (
        
          θ
          
            ⊤
          
        
        x
        )
        =
        
          
            1
            
              1
              +
              exp
              ⁡
              (
              −
              
                
                  θ
                
                
                  ⊤
                
              
              
                x
              
              )
            
          
        
      
    
    {\displaystyle h_{\theta }(x)=g(\theta ^{\top }x)={\frac {1}{1+\exp(-{\boldsymbol {\theta }}^{\top }\mathbf {x} )}}}
  

Da g(z) immer Werte zwischen 0 und 1 liefert, liegen auch die Werte von 
  
    
      
        h
        (
        x
        )
      
    
    {\displaystyle h(x)}
  
 zwischen 0 und 1. Dies lässt sich im folgenden Graphen erkennen:

Die Einteilung einer Beobachtung in eine bestimmte Klasse erfolgt folgendermaßen:

  
    
      
        g
        (
        z
        )
        ≥
        0
        
          ,
        
        5
        ⇒
        Y
        =
        1
      
    
    {\displaystyle g(z)\geq 0{,}5\Rightarrow Y=1}
  

  
    
      
        g
        (
        z
        )
        <
        0
        
          ,
        
        5
        ⇒
        Y
        =
        0
      
    
    {\displaystyle g(z)<0{,}5\Rightarrow Y=0}
  

Um eine möglichst akkurate Zuordnung der Datenpunkte zu den Zielklassen zu erreichen, werden die Parameter, ähnlich wie bei der linearen Regression, mit Hilfe einer geeigneten Funktion optimiert.
Wir nehmen dazu den folgenden Zusammenhang an:

  
    
      
        P
        (
        y
        =
        1
        ∣
        x
        ;
        θ
        )
        =
        
          h
          
            θ
          
        
        (
        x
        )
      
    
    {\displaystyle P(y=1\mid x;\theta )=h_{\theta }(x)}
  

  
    
      
        P
        (
        y
        =
        0
        ∣
        x
        ;
        θ
        )
        =
        1
        −
        
          h
          
            θ
          
        
        (
        x
        )
      
    
    {\displaystyle P(y=0\mid x;\theta )=1-h_{\theta }(x)}
  

Diese Gleichungen bedeuten, dass die Wahrscheinlichkeit, dass ein gegebener Datenpunkt der Klasse 1 angehört, durch das Ergebnis der Hypothesenfunktion 
  
    
      
        h
        (
        x
        )
      
    
    {\displaystyle h(x)}
  
 gegeben ist.
Daraus folgt, dass die allgemeine bedingte Wahrscheinlichkeit für einen bestimmten Output y für einen gegebenen Datenpunkt x durch die folgende Funktion gegeben ist:

  
    
      
        p
        (
        y
        ∣
        x
        ;
        θ
        )
        =
        (
        
          h
          
            θ
          
        
        (
        x
        )
        
          )
          
            y
          
        
        (
        1
        −
        
          h
          
            θ
          
        
        (
        x
        )
        
          )
          
            1
            −
            y
          
        
      
    
    {\displaystyle p(y\mid x;\theta )=(h_{\theta }(x))^{y}(1-h_{\theta }(x))^{1-y}}
  

Multipliziert man diese Wahrscheinlichkeit nun für alle Trainingsdatenpunkte, erhält man die Formel für die sogenannte „Likelihood“ eines bestimmten Parameters.

  
    
      
        L
        (
        θ
        )
        =
        p
        (
        
          y
        
        ∣
        X
        ;
        θ
        )
      
    
    {\displaystyle L(\theta )=p(\mathbf {y} \mid X;\theta )}
  

  
    
      
        =
        
          ∏
          
            i
            =
            1
          
          
            m
          
        
        p
        (
        
          y
          
            (
            i
            )
          
        
        ∣
        
          x
          
            (
            i
            )
          
        
        ;
        θ
        )
      
    
    {\displaystyle =\prod _{i=1}^{m}p(y^{(i)}\mid x^{(i)};\theta )}
  

  
    
      
        =
        
          ∏
          
            i
            =
            1
          
          
            m
          
        
        (
        
          h
          
            θ
          
        
        (
        
          x
          
            (
            i
            )
          
        
        )
        
          )
          
            
              y
              
                (
                i
                )
              
            
          
        
        (
        1
        −
        
          h
          
            θ
          
        
        (
        
          x
          
            (
            i
            )
          
        
        )
        
          )
          
            1
            −
            
              y
              
                (
                i
                )
              
            
          
        
      
    
    {\displaystyle =\prod _{i=1}^{m}(h_{\theta }(x^{(i)}))^{y^{(i)}}(1-h_{\theta }(x^{(i)}))^{1-y^{(i)}}}
  

Hat man bei der linearen Regression die mittlere quadratische Abweichung minimiert, um die optimalen Werte für die Parameter zu erhalten, maximiert man bei der logistischen Regression die Likelihood-Funktion, um die optimalen Werte der Parameter zu erhalten. Dieses Verfahren wird als Maximum-Likelihood-Methode bezeichnet.
Um die Maximierung zu erleichtern, wird oft auch die Log-Likelihood-Funktion gebildet:

  
    
      
        ℓ
        (
        θ
        )
        =
        log
        ⁡
        L
        (
        θ
        )
      
    
    {\displaystyle \ell (\theta )=\log L(\theta )}
  

  
    
      
        =
        
          ∑
          
            i
            =
            1
          
          
            m
          
        
        
          y
          
            (
            i
            )
          
        
        log
        ⁡
        h
        (
        
          x
          
            (
            i
            )
          
        
        )
        +
        (
        1
        −
        
          y
          
            (
            i
            )
          
        
        )
        log
        ⁡
        (
        1
        −
        h
        (
        
          x
          
            (
            i
            )
          
        
        )
        )
      
    
    {\displaystyle =\sum _{i=1}^{m}y^{(i)}\log h(x^{(i)})+(1-y^{(i)})\log(1-h(x^{(i)}))}
  

Von dieser Funktion muss nun die Steigung berechnet werden, wozu der sogenannte gradient ascent verwendet wird. Er funktioniert ähnlich wie das bei der linearen Regression angewendete Gradientenverfahren, außer dass er eine Addition anstatt einer Subtraktion durchführt, da die Log-Likelihood-Funktion maximiert und nicht minimiert werden soll. Durch die folgende Gleichung erhält man somit den optimierten Wert des Parameters:

  
    
      
        
          θ
          
            j
          
        
        :=
        
          θ
          
            j
          
        
        +
        α
        (
        
          y
          
            (
            i
            )
          
        
        −
        
          h
          
            θ
          
        
        (
        
          x
          
            (
            i
            )
          
        
        )
        )
        
          x
          
            j
          
          
            (
            i
            )
          
        
      
    
    {\displaystyle \theta _{j}:=\theta _{j}+\alpha (y^{(i)}-h_{\theta }(x^{(i)}))x_{j}^{(i)}}

### Perzeptron-Algorithmus

In den 1960er Jahren wurde der sogenannte Perzeptron-Algorithmus entwickelt. Er wurde entsprechend den Vorstellungen der damaligen Zeit über die Funktionsweise des Gehirns aufgebaut.
Der wesentliche Unterschied zwischen dem Perzepton Algorithmus und der logistischen Regression ist, dass die Funktion 
  
    
      
        h
        (
        x
        )
      
    
    {\displaystyle h(x)}
  
 entweder den Wert 0 oder den Wert 1 annimmt, aber nicht wie bei der logistischen Regression einen beliebigen Wert zwischen 0 und 1. Dies wird sichergestellt, indem die Funktion 
  
    
      
        g
        (
        z
        )
      
    
    {\displaystyle g(z)}
  
 nicht wie bei der logistischen Regression mit Hilfe einer Sigmoid Funktion einen Wert zwischen 0 und 1 annimmt, sondern entsprechend der Formeln:

  
    
      
        g
        (
        z
        )
        =
        1
      
    
    {\displaystyle g(z)=1}
  
 wenn 
  
    
      
        z
        ≥
        0
      
    
    {\displaystyle z\geq 0}
  

  
    
      
        g
        (
        z
        )
        =
        0
      
    
    {\displaystyle g(z)=0}
  
 wenn 
  
    
      
        z
        <
        0
      
    
    {\displaystyle z<0}
  

entweder genau 0 oder genau 1 entspricht.
Es gilt weiterhin:

  
    
      
        
          h
          
            θ
          
        
        (
        x
        )
        =
        g
        (
        
          
            θ
          
          
            ⊤
          
        
        
          x
        
        )
      
    
    {\displaystyle h_{\theta }(x)=g({\boldsymbol {\theta }}^{\top }\mathbf {x} )}
  

Und die Updating Regel ist ebenfalls beschrieben durch:

  
    
      
        
          θ
          
            j
          
        
        :=
        
          θ
          
            j
          
        
        +
        α
        (
        
          y
          
            (
            i
            )
          
        
        −
        
          h
          
            θ
          
        
        (
        
          x
          
            (
            i
            )
          
        
        )
        )
        
          x
          
            j
          
          
            (
            i
            )
          
        
      
    
    {\displaystyle \theta _{j}:=\theta _{j}+\alpha (y^{(i)}-h_{\theta }(x^{(i)}))x_{j}^{(i)}}
  

Diese Gleichung sieht sehr ähnlich aus zu den Lernprozessen der vorherigen Algorithmen. Es muss jedoch beachtet werden, dass durch die Definition von 
  
    
      
        g
        (
        z
        )
      
    
    {\displaystyle g(z)}
  
 Perzeptron einen nicht sonderlich fließenden Lernprozess hat, da der Fehler, der entsteht, wenn ein Input durch den Algorithmus falsch klassifiziert wird, entweder wesentlich überschätzt oder unterschätzt werden kann, in dem 
  
    
      
        h
        (
        x
        )
      
    
    {\displaystyle h(x)}
  
 nur 1 oder 0 annehmen kann. So wird beispielsweise, wenn 
  
    
      
        z
        =
        −
        0,000
        1
      
    
    {\displaystyle z=-0{,}0001}
  
 beträgt sowie wenn 
  
    
      
        z
        =
        −
        100
      
    
    {\displaystyle z=-100}
  
 beträgt in beiden Fällen die Klasse 0 vorhergesagt. Gehören die Beobachtungen allerdings in Wahrheit Klasse 1 an, so werden die Parameter in beiden Fällen, um den gleichen Wert angepasst.

### Weitere Beispiele für überwachte Lernalgorithmen zur Klassifikation

Bayes-Klassifikator
Naiver Bayes-Klassifikator
Nächste-Nachbarn-Klassifikation
Diskriminanzanalyse
Künstliches neuronales Netz
Gradient Boosted Trees (Entscheidungsbaum)
