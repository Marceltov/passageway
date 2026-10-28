---
title: Gradientenverfahren
url: https://de.wikipedia.org/wiki/Gradientenverfahren
updated: '2026-09-27T11:27:20Z'
language: de
revision: '270825489'
license: CC BY-SA 4.0
source: Wikipedia
---

Ein Gradientenverfahren ist ein numerisches Verfahren im Bereich der Optimierung. Ein solches Verfahren beschreibt einen Algorithmus zur Lösung eines Optimierungsproblems, bei welchem der Gradient zur Bestimmung der Suchrichtung verwendet wird.
Das einfachste Gradientenverfahren ist das Verfahren des steilsten Abstiegs. Es wird in der Literatur häufig synonym als das Gradientenverfahren bezeichnet. In der englischsprachigen Fachliteratur ist es unter dem Namen steepest descent method oder gradient descent zu finden. Das Verfahren ist nicht zu verwechseln mit der analytischen Methode des steilsten Abstiegs in der Analysis und asymptotischen Analysis. 
Für ein Minimierungsproblem ist die Idee des Verfahrens, von einem Startpunkt aus entlang einer Abstiegsrichtung schrittweise (iterativ) Punkte zu finden, für die der Wert der zu minimierenden Funktion kleiner und schlussendlich minimal wird. Als Abstiegsrichtung wird in diesem Falle direkt der negative Gradient, also die Richtung des lokal steilsten Abstiegs, verwendet (Gradientenabstieg). Bei einem Maximierungsproblem kann entsprechend der positive Gradient verwendet werden.
Das Verfahren des steilsten Abstiegs konvergiert oftmals vergleichsweise langsam, da es sich dem stationären Punkt mit einem stark oszillierenden Kurs nähert. Es existieren weitere Methoden für die Berechnung der Abstiegsrichtung auf Basis des Gradienten (Methoden 1. Ordnung), wie beispielsweise das Verfahren der konjugierten Gradienten. Diese erreichen teils deutlich bessere Konvergenzgeschwindigkeiten.

## Das Verfahren

Ausgangspunkt ist das Minimierungsproblem

  
    
      
        
          
            min
            
              x
              ∈
              
                
                  R
                
                
                  n
                
              
            
          
        
         
        f
        (
        x
        )
      
    
    {\displaystyle {\underset {x\in \mathbb {R} ^{n}}{\min }}\ f(x)}
  

für eine reellwertige, differenzierbare Funktion 
  
    
      
        f
        :
        
          
            R
          
          
            n
          
        
        →
        
          R
        
        .
      
    
    {\displaystyle f\colon \mathbb {R} ^{n}\rightarrow \mathbb {R} .}
  
 Hierbei handelt es sich um ein Problem der Optimierung ohne Nebenbedingungen, auch unrestringiertes Optimierungsproblem genannt.
Das Gradientenverfahren generiert ausgehend von einem Startpunkt 
  
    
      
        
          x
          
            0
          
        
        ∈
        
          
            R
          
          
            n
          
        
      
    
    {\displaystyle x^{0}\in \mathbb {R} ^{n}}
  
 eine Folge von Punkten 
  
    
      
        
          x
          
            k
          
        
        ∈
        
          
            R
          
          
            n
          
        
      
    
    {\displaystyle x^{k}\in \mathbb {R} ^{n}}
  
 gemäß der Iterationsvorschrift

wobei 
  
    
      
        
          α
          
            k
          
        
        >
        0
      
    
    {\displaystyle \alpha ^{k}>0}
  
 eine positive Schrittweite ist und 
  
    
      
        
          d
          
            k
          
        
        ∈
        
          
            R
          
          
            n
          
        
      
    
    {\displaystyle d^{k}\in \mathbb {R} ^{n}}
  
 eine Abstiegsrichtung. Dabei werden sowohl 
  
    
      
        
          α
          
            k
          
        
      
    
    {\displaystyle \alpha ^{k}}
  
 als auch 
  
    
      
        
          d
          
            k
          
        
      
    
    {\displaystyle d^{k}}
  
 in jedem Iterationsschritt so bestimmt, dass die Folge 
  
    
      
        
          x
          
            k
          
        
      
    
    {\displaystyle x^{k}}
  
 zu einem stationären Punkt von 
  
    
      
        f
      
    
    {\displaystyle f}
  
 konvergiert.

### Bestimmen der Abstiegsrichtung

Eine Abstiegsrichtung im Punkt 
  
    
      
        
          x
          
            k
          
        
      
    
    {\displaystyle x^{k}}
  
 ist ein Vektor 
  
    
      
        
          d
          
            k
          
        
      
    
    {\displaystyle d^{k}}
  
, der

  
    
      
        
          
            (
            
              ∇
              f
              (
              
                x
                
                  k
                
              
              )
            
            )
          
          
            T
          
        
        
          d
          
            k
          
        
        <
        0
      
    
    {\displaystyle \left(\nabla f(x^{k})\right)^{T}d^{k}<0}
  

erfüllt. Intuitiv bedeutet das, dass der Winkel zwischen 
  
    
      
        ∇
        f
        (
        
          x
          
            k
          
        
        )
      
    
    {\displaystyle \nabla f(x^{k})}
  
 und 
  
    
      
        
          d
          
            k
          
        
      
    
    {\displaystyle d^{k}}
  
 größer als 90° ist. Da der Gradient 
  
    
      
        ∇
        f
        (
        
          x
          
            k
          
        
        )
      
    
    {\displaystyle \nabla f(x^{k})}
  
 in Richtung des steilsten Anstiegs zeigt, ist 
  
    
      
        
          d
          
            k
          
        
      
    
    {\displaystyle d^{k}}
  
 eine Richtung entlang derer sich der Funktionswert verringert.
Viele Gradientenmethoden berechnen die Abstiegsrichtung anhand

  
    
      
        
          d
          
            k
          
        
        =
        −
        
          D
          
            k
          
        
        ∇
        f
        (
        
          x
          
            k
          
        
        )
        ,
      
    
    {\displaystyle d^{k}=-D^{k}\nabla f(x^{k}),}
  

wobei 
  
    
      
        
          D
          
            k
          
        
      
    
    {\displaystyle D^{k}}
  
 eine positiv definite Matrix ist. In diesem Fall lautet die Bedingung für die Abstiegsrichtung

  
    
      
        
          
            (
            
              ∇
              f
              (
              
                x
                
                  k
                
              
              )
            
            )
          
          
            T
          
        
        
          (
          
            −
            
              D
              
                k
              
            
          
          )
        
        ∇
        f
        (
        
          x
          
            k
          
        
        )
        <
        0
        ,
      
    
    {\displaystyle \left(\nabla f(x^{k})\right)^{T}\left(-D^{k}\right)\nabla f(x^{k})<0,}
  

und ist dank der positiven Definitheit von 
  
    
      
        
          D
          
            k
          
        
      
    
    {\displaystyle D^{k}}
  
 immer erfüllt.
Mit der Wahl der Matrix 
  
    
      
        
          D
          
            k
          
        
      
    
    {\displaystyle D^{k}}
  
 erhält man folgende Algorithmen:

  
    
      
        
          D
          
            k
          
        
        =
        I
      
    
    {\displaystyle D^{k}=I}
  
, wobei 
  
    
      
        I
      
    
    {\displaystyle I}
  
 die Einheitsmatrix ist, ergibt das Verfahren des steilsten Abstiegs. Die Abstiegsrichtung ist in diesem Fall einfach der negative Gradient, 
  
    
      
        
          d
          
            k
          
        
        =
        −
        ∇
        f
        (
        
          x
          
            k
          
        
        )
      
    
    {\displaystyle d^{k}=-\nabla f(x^{k})}
  
.

  
    
      
        
          D
          
            k
          
        
        =
        
          
            [
            
              
                
                  
                    a
                    
                      1
                    
                  
                
                
                  0
                
                
                  ⋯
                
                
                  0
                
              
              
                
                  0
                
                
                  
                    a
                    
                      2
                    
                  
                
                
                  ⋱
                
                
                  ⋮
                
              
              
                
                  ⋮
                
                
                  ⋱
                
                
                  ⋱
                
                
                  0
                
              
              
                
                  0
                
                
                  ⋯
                
                
                  0
                
                
                  
                    a
                    
                      n
                    
                  
                
              
            
            ]
          
        
      
    
    {\displaystyle D^{k}={\begin{bmatrix}a_{1}&0&\cdots &0\\0&a_{2}&\ddots &\vdots \\\vdots &\ddots &\ddots &0\\0&\cdots &0&a_{n}\end{bmatrix}}}
  
, wobei 
  
    
      
        
          a
          
            i
          
        
        >
        0
        ,
         
        i
        =
        1
        ,
        …
        ,
        n
      
    
    {\displaystyle a_{i}>0,\ i=1,\ldots ,n}
  
 sodass 
  
    
      
        
          D
          
            k
          
        
      
    
    {\displaystyle D^{k}}
  
 positiv definit ist, ist ein diagonal skalierter steilster Abstieg. Oft werden die 
  
    
      
        
          a
          
            i
          
        
      
    
    {\displaystyle a_{i}}
  
 als Approximation der Inversen der 2. Ableitung gewählt, also 
  
    
      
        
          a
          
            i
          
        
        ≈
        
          
            (
            
              
                
                  
                    ∂
                    
                      2
                    
                  
                  f
                  (
                  
                    x
                    
                      k
                    
                  
                  )
                
                
                  
                    (
                    
                      ∂
                      
                        x
                        
                          i
                        
                      
                    
                    )
                  
                  
                    2
                  
                
              
            
            )
          
          
            −
            1
          
        
      
    
    {\displaystyle a_{i}\approx \left({\frac {\partial ^{2}f(x^{k})}{\left(\partial x_{i}\right)^{2}}}\right)^{-1}}
  
.

  
    
      
        
          D
          
            k
          
        
        =
        
          
            (
            
              
                ∇
                
                  2
                
              
              f
              (
              
                x
                
                  k
                
              
              )
            
            )
          
          
            −
            1
          
        
      
    
    {\displaystyle D^{k}=\left(\nabla ^{2}f(x^{k})\right)^{-1}}
  
, die Inverse Hesse-Matrix, ergibt das Newton-Verfahren für die Lösung nichtlinearer Minimierungsprobleme.
Da die Berechnung der Hesse-Matrix oft aufwändig ist, gibt es eine Klasse von Algorithmen, welche eine Approximation 
  
    
      
        
          D
          
            k
          
        
        ≈
        
          
            (
            
              
                ∇
                
                  2
                
              
              f
              (
              x
              )
            
            )
          
          
            −
            1
          
        
      
    
    {\displaystyle D^{k}\approx \left(\nabla ^{2}f(x)\right)^{-1}}
  
 verwenden. Solche Methoden werden als Quasi-Newton-Verfahren bezeichnet, es gibt verschiedene Arten wie die Approximation berechnet wird. Ein wichtiger Vertreter aus der Klasse der Quasi-Newton Methoden ist der BFGS Algorithmus.
Falls das Optimierungsproblem in der speziellen Form

  
    
      
        
          min
          
            x
            ∈
            
              
                R
              
              
                n
              
            
          
        
        
          {
          
            ‖
            f
            (
            x
            )
            
              ‖
              
                2
              
            
            =
            
              ∑
              
                i
                =
                1
              
              
                m
              
            
            
              
                (
                
                  
                    f
                    
                      i
                    
                  
                  (
                  x
                  )
                
                )
              
              
                2
              
            
          
          }
        
      
    
    {\displaystyle \min _{x\in \mathbb {R} ^{n}}\left\{\|f(x)\|^{2}=\sum _{i=1}^{m}\left(f_{i}(x)\right)^{2}\right\}}
  
,
also als Summe von Quadraten von Funktionen, gegeben ist, erhält man mit 
  
    
      
        
          D
          
            k
          
        
        =
        
          
            (
            
              
                J
                
                  T
                
              
              J
            
            )
          
          
            −
            1
          
        
      
    
    {\displaystyle D^{k}=\left(J^{T}J\right)^{-1}}
  
, wobei 
  
    
      
        J
      
    
    {\displaystyle J}
  
 die Jacobi-Matrix von 
  
    
      
        f
      
    
    {\displaystyle f}
  
 im Punkt 
  
    
      
        
          x
          
            k
          
        
      
    
    {\displaystyle x^{k}}
  
 ist, das Gauß-Newton-Verfahren.

### Bestimmen der Schrittweite

Die Bestimmung der Schrittweite 
  
    
      
        
          α
          
            k
          
        
      
    
    {\displaystyle \alpha ^{k}}
  
 ist ein wichtiger Teil des Gradientenverfahren, der großen Einfluss auf die Konvergenz haben kann. Ausgehend vom Iterationsschritt 
  
    
      
        
          x
          
            k
            +
            1
          
        
        =
        
          x
          
            k
          
        
        +
        
          α
          
            k
          
        
        
          d
          
            k
          
        
      
    
    {\displaystyle x^{k+1}=x^{k}+\alpha ^{k}d^{k}}
  
 betrachtet man den Wert von 
  
    
      
        f
      
    
    {\displaystyle f}
  
 entlang der Linie 
  
    
      
        
          x
          
            k
          
        
        +
        α
        
          d
          
            k
          
        
      
    
    {\displaystyle x^{k}+\alpha d^{k}}
  
, also 
  
    
      
        f
        (
        α
        )
        =
        f
        (
        
          x
          
            k
          
        
        +
        α
        
          d
          
            k
          
        
        )
      
    
    {\displaystyle f(\alpha )=f(x^{k}+\alpha d^{k})}
  
. Man spricht in diesem Zusammenhang oft auch von Liniensuche. Die ideale Wahl wäre es, die Schrittweite als jenen Wert zu berechnen, der die Funktion 
  
    
      
        f
        (
        α
        )
      
    
    {\displaystyle f(\alpha )}
  
 minimiert, also das eindimensionale Problem

  
    
      
        
          min
          
            α
            >
            0
          
        
        
          {
          
            f
            (
            α
            )
            =
            f
            (
            
              x
              
                k
              
            
            +
            α
            
              d
              
                k
              
            
            )
          
          }
        
      
    
    {\displaystyle \min _{\alpha >0}\left\{f(\alpha )=f(x^{k}+\alpha d^{k})\right\}}
  

zu lösen. Dies wird als exakte Liniensuche bezeichnet und wird in dieser Form in der Praxis selten angewandt, da selbst für einfache Optimierungsprobleme die exakte Bestimmung der Schrittweite sehr rechenaufwändig ist.
Als Alternative zur exakten Liniensuche lockert man die Erfordernisse und beschränkt sich darauf, dass der Funktionswert sich mit jedem Iterationsschritt „genügend“ verringert. Dies wird auch als inexakte Liniensuche bezeichnet. Die einfachste Möglichkeit besteht darin, die Schrittweite 
  
    
      
        α
      
    
    {\displaystyle \alpha }
  
 ausgehend von einem Startwert (z. B. 
  
    
      
        α
        =
        1
      
    
    {\displaystyle \alpha =1}
  
) so lange zu verringern, bis 
  
    
      
        f
        (
        
          x
          
            k
            +
            1
          
        
        )
        =
        f
        (
        
          x
          
            k
          
        
        +
        α
        
          d
          
            k
          
        
        )
        <
        f
        (
        
          x
          
            k
          
        
        )
      
    
    {\displaystyle f(x^{k+1})=f(x^{k}+\alpha d^{k})<f(x^{k})}
  
 erreicht ist. Diese Methode funktioniert in der Praxis oft zufriedenstellend, man kann jedoch zeigen, dass für manche pathologischen Funktionen diese Liniensuche zwar in jedem Schritt den Funktionswert verringert, die Folge 
  
    
      
        
          x
          
            k
          
        
      
    
    {\displaystyle x^{k}}
  
 jedoch nicht zu einem stationären Punkt konvergiert.

#### Armijo-Bedingung

Die Armijo-Bedingung formalisiert das Konzept „genügend“ in der geforderten Verringerung des Funktionswertes. Die Bedingung 
  
    
      
        f
        (
        
          x
          
            k
          
        
        +
        α
        
          d
          
            k
          
        
        )
        <
        f
        (
        
          x
          
            k
          
        
        )
      
    
    {\displaystyle f(x^{k}+\alpha d^{k})<f(x^{k})}
  
 wird modifiziert zu

  
    
      
        f
        (
        
          x
          
            k
          
        
        +
        α
        
          d
          
            k
          
        
        )
        ≤
        f
        (
        
          x
          
            k
          
        
        )
        +
        σ
        α
        
          
            (
            
              ∇
              f
              (
              
                x
                
                  k
                
              
              )
            
            )
          
          
            T
          
        
        
          d
          
            k
          
        
        ,
      
    
    {\displaystyle f(x^{k}+\alpha d^{k})\leq f(x^{k})+\sigma \alpha \left(\nabla f(x^{k})\right)^{T}d^{k},}
  

mit 
  
    
      
        σ
        ∈
        (
        0
        ,
        1
        )
      
    
    {\displaystyle \sigma \in (0,1)}
  
. Die Armijo-Bedingung umgeht die Konvergenzprobleme aus der vorigen einfachen Bedingung, indem sie fordert, dass die Verringerung zumindest proportional zur Schrittweite und zur Richtungsableitung 
  
    
      
        
          
            (
            
              ∇
              f
              (
              
                x
                
                  k
                
              
              )
            
            )
          
          
            T
          
        
        
          d
          
            k
          
        
      
    
    {\displaystyle \left(\nabla f(x^{k})\right)^{T}d^{k}}
  
 ist, mit Proportionalitätskonstante 
  
    
      
        σ
      
    
    {\displaystyle \sigma }
  
. In der Praxis werden oft sehr kleine Werte verwendet, z. B. 
  
    
      
        σ
        =
        
          10
          
            −
            4
          
        
      
    
    {\displaystyle \sigma =10^{-4}}
  
.

#### Backtracking-Liniensuche

Die Armijo-Bedingung gilt immer dann, wenn die Schrittweite genügend klein ist und kann damit zum Stillstand des Gradientenverfahrens führen – der Schritt ist so klein, dass kein nennenswerter Fortschritt mehr gemacht wird. Eine einfache Kombination aus wiederholter Verkleinerung der Schrittweite und der Armijo-Bedingung ist die Backtracking-Liniensuche. Sie stellt sicher, dass die Schrittweite klein genug ist, um die Armijo-Bedingung zu erfüllen, andererseits aber nicht zu klein. In Pseudocode:

Wähle Startwert für 
  
    
      
        α
      
    
    {\displaystyle \alpha }
  
, z. B. 
  
    
      
        α
        =
        1
      
    
    {\displaystyle \alpha =1}
  
, wähle Konstanten 
  
    
      
        σ
        ∈
        (
        0
        ,
        1
        )
        ,
         
        ρ
        ∈
        (
        0
        ,
        1
        )
      
    
    {\displaystyle \sigma \in (0,1),\ \rho \in (0,1)}
  

while 
  
    
      
        f
        (
        
          x
          
            k
          
        
        +
        α
        
          d
          
            k
          
        
        )
        >
        f
        (
        
          x
          
            k
          
        
        )
        +
        σ
        α
        
          
            (
            
              ∇
              f
              (
              
                x
                
                  k
                
              
              )
            
            )
          
          
            T
          
        
        
          d
          
            k
          
        
      
    
    {\displaystyle f(x^{k}+\alpha d^{k})>f(x^{k})+\sigma \alpha \left(\nabla f(x^{k})\right)^{T}d^{k}}
  

  
  
    
      
        α
        =
        ρ
        α
      
    
    {\displaystyle \alpha =\rho \alpha }
  

end

Setze 
  
    
      
        
          α
          
            k
          
        
        =
        α
      
    
    {\displaystyle \alpha ^{k}=\alpha }
  

Die Backtracking-Liniensuche verringert die Schrittweite wiederholt um den Faktor 
  
    
      
        ρ
      
    
    {\displaystyle \rho }
  
, bis die Armijo-Bedingung erfüllt ist. Sie terminiert garantiert nach einer endlichen Anzahl von Schritten und wird wegen ihrer Einfachheit oft in Praxis verwendet.

## Konvergenz

Im Allgemeinen konvergiert das Gradientenverfahren weder zu einem globalen noch zu einem lokalen Minimum. Garantiert werden kann nur die Konvergenz zu einem stationären Punkt, also einem Punkt 
  
    
      
        
          x
          
            ∗
          
        
      
    
    {\displaystyle x^{*}}
  
mit 
  
    
      
        ∇
        f
        (
        
          x
          
            ∗
          
        
        )
        =
        0
      
    
    {\displaystyle \nabla f(x^{*})=0}
  
. Schränkt man die Klasse der Zielfunktionen auf konvexe Funktionen ein, so sind stärkere Garantien möglich, siehe konvexe Optimierung.
Für den allgemeinen Fall kann weder über die Konvergenzgeschwindigkeit der Folge 
  
    
      
        {
        f
        (
        
          x
          
            k
          
        
        )
        }
      
    
    {\displaystyle \{f(x^{k})\}}
  
 noch über die Konvergenzgeschwindigkeit der Folge 
  
    
      
        {
        
          x
          
            k
          
        
        }
      
    
    {\displaystyle \{x^{k}\}}
  
 eine Aussage getroffen werden. Ist 
  
    
      
        L
      
    
    {\displaystyle L}
  
 eine Lipschitz-Konstante von 
  
    
      
        ∇
        f
      
    
    {\displaystyle \nabla f}
  
, so kann man zeigen, dass die Norm der Gradienten 
  
    
      
        
          g
          
            N
          
          
            ∗
          
        
        =
        
          min
          
            0
            ≤
            k
            ≤
            N
          
        
        ‖
        ∇
        f
        (
        
          x
          
            k
          
        
        )
        ‖
      
    
    {\displaystyle g_{N}^{*}=\min _{0\leq k\leq N}\|\nabla f(x^{k})\|}
  
 mit der Rate

  
    
      
        
          
            
              
                L
                
                  (
                  
                    f
                    (
                    
                      x
                      
                        0
                      
                    
                    )
                    −
                    f
                    (
                    
                      x
                      
                        ∗
                      
                    
                    )
                  
                  )
                
              
              
                ω
                (
                N
                +
                1
                )
              
            
          
        
      
    
    {\displaystyle {\sqrt {\frac {L\left(f(x^{0})-f(x^{*})\right)}{\omega (N+1)}}}}
  

gegen 0 konvergiert, wobei 
  
    
      
        ω
        >
        0
      
    
    {\displaystyle \omega >0}
  
 eine positive Konstante ist.

## Beispiel

Die Rosenbrock-Funktion

  
    
      
        f
        :
        
          
            R
          
          
            2
          
        
        →
        
          R
        
        :
        x
        ↦
        
          
            (
            
              a
              −
              
                x
                
                  1
                
              
            
            )
          
          
            2
          
        
        +
        b
        
          
            (
            
              
                x
                
                  2
                
              
              −
              
                x
                
                  1
                
                
                  2
                
              
            
            )
          
          
            2
          
        
      
    
    {\displaystyle f:\mathbb {R} ^{2}\to \mathbb {R} :x\mapsto \left(a-x_{1}\right)^{2}+b\left(x_{2}-x_{1}^{2}\right)^{2}}
  

wird häufig als Test für Optimierungsmethoden verwendet, da sie wegen des schmalen und flachen Tals, in welchem iterative Methoden nur kleine Schritte machen können, eine Herausforderung darstellt. Die Konstanten werden üblicherweise mit 
  
    
      
        a
        =
        1
        ,
         
        b
        =
        100
      
    
    {\displaystyle a=1,\ b=100}
  
 gewählt, das globale Optimum liegt in diesem Fall bei 
  
    
      
        
          x
          
            ∗
          
        
        =
        (
        1
        ,
        1
        )
      
    
    {\displaystyle x^{*}=(1,1)}
  
 mit dem Funktionswert 
  
    
      
        f
        (
        
          x
          
            ∗
          
        
        )
        =
        0
      
    
    {\displaystyle f(x^{*})=0}
  
.
Der Gradient sowie die Hesse-Matrix ergeben sich als

  
    
      
        ∇
        f
        =
        
          
            [
            
              
                
                  4
                  b
                  
                    x
                    
                      1
                    
                    
                      3
                    
                  
                  −
                  4
                  b
                  
                    x
                    
                      1
                    
                  
                  
                    x
                    
                      2
                    
                  
                  +
                  2
                  (
                  
                    x
                    
                      1
                    
                  
                  −
                  a
                  )
                
              
              
                
                  2
                  b
                  (
                  −
                  
                    x
                    
                      1
                    
                    
                      2
                    
                  
                  +
                  
                    x
                    
                      2
                    
                  
                  )
                
              
            
            ]
          
        
      
    
    {\displaystyle \nabla f={\begin{bmatrix}4bx_{1}^{3}-4bx_{1}x_{2}+2(x_{1}-a)\\2b(-x_{1}^{2}+x_{2})\end{bmatrix}}}
  

sowie

  
    
      
        
          ∇
          
            2
          
        
        f
        =
        
          
            [
            
              
                
                  12
                  b
                  
                    x
                    
                      1
                    
                    
                      2
                    
                  
                  −
                  4
                  b
                  
                    x
                    
                      2
                    
                  
                  +
                  2
                
                
                  −
                  4
                  b
                  
                    x
                    
                      1
                    
                  
                
              
              
                
                  −
                  4
                  b
                  
                    x
                    
                      1
                    
                  
                
                
                  2
                  b
                
              
            
            ]
          
        
      
    
    {\displaystyle \nabla ^{2}f={\begin{bmatrix}12bx_{1}^{2}-4bx_{2}+2&-4bx_{1}\\-4bx_{1}&2b\end{bmatrix}}}
  
.
Damit lassen sich die Algorithmen Verfahren des steilsten Abstiegs und Newton-Verfahren direkt implementieren. Um das Gauß-Newton-Verfahren anzuwenden, muss die Rosenbrock-Funktion zunächst in die Form „Summe von Quadraten von Funktionen“ gebracht werden. Dies ist auf der Seite zum Gauß-Newton-Verfahren im Detail erklärt.

Für die Liniensuche kommt bei allen Verfahren ein Backtracking mit folgenden Parametern zum Einsatz: Startwert 
  
    
      
        α
        =
        1
      
    
    {\displaystyle \alpha =1}
  
, 
  
    
      
        ρ
        =
        0
        
          ,
        
        5
      
    
    {\displaystyle \rho =0{,}5}
  
, 
  
    
      
        σ
        =
        0,001
      
    
    {\displaystyle \sigma =0{,}001}
  
. Als Startpunkt wird 
  
    
      
        
          x
          
            0
          
        
        =
        (
        −
        0
        
          ,
        
        62
        ;
        
        0
        
          ,
        
        38
        )
      
    
    {\displaystyle x^{0}=(-0{,}62;\,0{,}38)}
  
 gewählt.
Das Verfahren des steilsten Abstiegs findet auch nach 1000 Iterationen nicht zum globalen Optimum und steckt in dem flachen Tal fest, wo nur sehr kleine Schritte möglich sind. Im Gegensatz dazu finden sowohl das Newton-Verfahren als auch der Gauß-Newton-Algorithmus in wenigen Iterationen zum globalen Optimum.
