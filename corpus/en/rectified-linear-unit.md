---
title: Rectified linear unit
url: https://en.wikipedia.org/wiki/Rectified_linear_unit
updated: '2026-09-07T09:21:01Z'
language: en
revision: '1373687081'
license: CC BY-SA 4.0
source: Wikipedia
---

In the context of artificial neural networks, the rectifier or ReLU (rectified linear unit) activation function is an activation function defined as the non-negative part of its argument, i.e., the ramp function:

$\operatorname {ReLU} (x)=x^{+}=\max(0,x)={\frac {x+|x|}{2}}={\begin{cases}x&{\text{if }}x>0,\\0&x\leq 0\end{cases}}$

where 
$x$

 is the input to a neuron. This is analogous to half-wave rectification in electrical engineering.
ReLU is one of the most popular activation functions for artificial neural networks, and finds application in computer vision and speech recognition using deep neural nets and computational neuroscience.

## History

The ReLU was first used by Alston Householder in 1941 as a mathematical abstraction of biological neural networks.
Kunihiko Fukushima in 1969 used ReLU in the context of visual feature extraction in hierarchical neural networks. 
In 1998, Gregory Woodbury demonstrated that the rectified linear function could account for a broad range of emergent properties in the visual cortex. His work showed that a single unified model could drive the joint development of refined retinotopic maps, ocular dominance columns, and orientation selectivity. By utilizing the rectifier's "cutoff" property, Woodbury achieved a close quantitative fit to biological data, matching the spatial periodicities and topographic refinement patterns observed in macaque and cat cortical maps. Furthermore, he extended this framework to adult plasticity, accurately replicating the spatial and temporal dynamics of lesion-induced cortical reorganization. This research established that the rectified linear response was a necessary mechanism for the stable self-organisation and maintenance of complex, multi-feature neural maps. In 2000, Hahnloser et al. argued that ReLU approximates the biological relationship between neural firing rates and input current, in addition to enabling recurrent neural network dynamics to stabilise under weaker criteria.
Prior to 2010, most activation functions used were the logistic sigmoid (which is inspired by probability theory; see logistic regression) and its more numerically efficient counterpart, the hyperbolic tangent. Around 2010, the use of ReLU became common again.
Jarrett et al. (2009) noted that rectification by either absolute or ReLU (which they called "positive part") was critical for object recognition in convolutional neural networks (CNNs), specifically because it allows average pooling without neighboring filter outputs cancelling each other out. They hypothesized that the use of sigmoid or tanh was responsible for poor performance in previous CNNs.
Nair and Hinton (2010) made a theoretical argument that the softplus activation function should be used, in that the softplus function numerically approximates the sum of an exponential number of linear models that share parameters. They then proposed ReLU as a good approximation to it. Specifically, they began by considering a single binary neuron in a Boltzmann machine that takes 
$x$

 as input, and produces 1 as output with probability 
$\sigma (x)={\frac {1}{1+e^{-x}}}$

. They then considered extending its range of output by making infinitely many copies of it 
$X_{1},X_{2},X_{3},\dots $

, that all take the same input, offset by an amount 
$0.5,1.5,2.5,\dots $

, then their outputs are added together as 
$\sum _{i=1}^{\infty }X_{i}$

. They then demonstrated that 
$\sum _{i=1}^{\infty }X_{i}$

 is approximately equal to 
${\mathcal {N}}(\log(1+e^{x}),\sigma (x))$

, which is also approximately equal to 
$\operatorname {ReLU} ({\mathcal {N}}(x,\sigma (x)))$

, where 
${\mathcal {N}}$

 stands for the gaussian distribution.
They also argued for another reason for using ReLU: that it allows "intensity equivariance" in image recognition. That is, multiplying input image by a constant 
$k$

 multiplies the output also. In contrast, this is false for other activation functions like sigmoid or tanh. They found that ReLU activation allowed good empirical performance in restricted Boltzmann machines.
Glorot et al (2011) argued that ReLU has the following advantages over sigmoid or tanh:

ReLU is more similar to biological neurons' responses in their main operating regime.
ReLU avoids vanishing gradients.
ReLU is cheaper to compute.
ReLU creates sparse representation naturally, because many hidden units output exactly zero for a given input.
They also found empirically that deep networks trained with ReLU can achieve strong performance without unsupervised pre-training, especially on large, purely supervised tasks.
In 2017, the rectified linear function became a central component of the transformer architecture introduced in  the Vaswani et al paper "Attention Is All You Need". Within every transformer layer, ReLU is utilized in the position-wise feed-forward networks (FFN), defined by Equation 2 of their paper:

$\operatorname {FFN} (x)=\max(0,xW_{1}+b_{1})W_{2}+b_{2}$

This equation is foundational to the model's capacity; while the attention mechanism determines the relationships between tokens, the ReLU-based FFN performs the majority of the numerical computation and houses the bulk of the model's parameters. The efficiency and scalability of this rectified framework triggered a global technological revolution, enabling the development of Large Language Models that have had a profound economic impact. The industrial response to this architecture—including the massive expansion of AI-specific hardware and the birth of the generative AI sector—has positioned the Transformer as a cornerstone of 21st-century infrastructure. 
During the post 2017 period of rapid AI advancement, the rectified linear unit function has been key to achieving increased model performance and scaling due to the fact that it zeros out responses that are immaterial for a given stimuli, preventing them from accumulating in massive scale models. It is the complete silencing of the parts of the model found to be stimuli-irrelevant during learning that allows for scaling. As the stimuli-irrelevant proportion of the model becomes more massive, these highly numerous connections within the model would inevitably accumulate during scaling no matter how small each individual response is. Therefore, the rectified linear unit function, with its absolute zeroing property, enabled the scaling to hundred billion parameter models and beyond.
Early Transformer scaling giants like GPT-3 (2020) and Falcon-180B (2023) relied on the rectified linear unit function explicitly, while successors such as GPT-4 (2023) and Llama 3 (2024) utilized smoother variants like GELU or SwiGLU. These variants were used to improve training stability while fundamentally preserving the rectified principle of zeroing low responses. At the centre of modern artificial intelligence ReLU and its variants maintain absolute zero response across the bulk of the model at any one time, while maintaining approximately linear responses for stimuli-relevant connections enabling high performance on each specific cognitive task. This feature of activation sparsity has been critical for massive scaling and performance gains of AI models right up to the present day.

## Advantages

Advantages of ReLU include:

Sparse activation: for example, in a randomly initialized network, only about 50% of hidden units are activated (i.e. have a non-zero output).
Better gradient propagation: fewer vanishing gradient problems compared to sigmoidal activation functions that saturate in both directions.
Efficiency: only requires comparison and addition.
Scale-invariant (homogeneous, or "intensity equivariance"):

$\max(0,ax)=a\max(0,x){\text{ for }}a\geq 0$

.

## Potential problems

Possible downsides can include:

Non-differentiability at zero (however, it is differentiable anywhere else, and the value of the derivative at zero can be chosen to be 0 or 1 arbitrarily).
Not zero-centered: ReLU outputs are always non-negative. This can make it harder for the network to learn during backpropagation, because gradient updates tend to push weights in one direction (positive or negative). Batch normalization can help address this.
ReLU is unbounded.
Redundancy of the parametrization: Because ReLU is scale-invariant, the network computes the exact same function by scaling the weights and biases in front of a ReLU activation by 
$k$

, and the weights after by 
$1/k$

.
Dying ReLU: ReLU neurons can sometimes be pushed into states in which they become inactive for essentially all inputs. In this state, no gradients flow backward through the neuron, and so the neuron becomes stuck in a perpetually inactive state (it "dies"). This is a form of the vanishing gradient problem. In some cases, large numbers of neurons in a network can become stuck in dead states, effectively decreasing the model capacity and potentially even halting the learning process. This problem typically arises when the learning rate is set too high. It may be mitigated by using "leaky" ReLU instead, where a small positive slope is assigned for 
$x<0$

. However, depending on the task, performance may be reduced.

## Variants

### Piecewise-linear variants

Leaky ReLU (2014) allows a small, positive gradient when the unit is inactive, helping to mitigate the vanishing gradient problem. This gradient is defined by a parameter 
$\alpha $

, typically set to 0.01–0.3.

$f(x)={\begin{cases}x&x>0,\\\alpha x&x\leq 0,\end{cases}}\qquad f'(x)={\begin{cases}1&x>0,\\\alpha &x\leq 0.\end{cases}}$

The same function can also be expressed without the piecewise notation as:

$f(x)={\frac {1+\alpha }{2}}x+{\frac {1-\alpha }{2}}|x|$

Parametric ReLU (PReLU, 2016) takes this idea further by making 
$\alpha $

 a learnable parameter along with the other network parameters.
Note that for 
$\alpha \leq 1$

, this is equivalent to

$f(x)=\max(x,\alpha x)$

and thus has a relation to "maxout" networks.
Concatenated ReLU (CReLU, 2016) preserves positive and negative phase information by returning two values:

$f(x)=[\operatorname {ReLU} (x),\operatorname {ReLU} (-x)].$

### Smooth variants

#### Softplus

A smooth approximation to the rectifier is the analytic function

$f(x)=\ln(1+e^{x}),\qquad f'(x)={\frac {e^{x}}{1+e^{x}}}={\frac {1}{1+e^{-x}}}$

which is called the softplus (2000) or SmoothReLU function. For large negative 
$x$

 it is roughly 
$\ln 1$

, so just above 0, while for large positive 
$x$

 it is roughly 
$\ln(e^{x})$

, so just above 
$x$

.
This function can be approximated as:

$\ln \left(1+e^{x}\right)\approx {\begin{cases}\ln 2,&x=0,\\[6pt]{\frac {x}{1-e^{-x/\ln 2}}},&x\neq 0\end{cases}}$

By making the change of variables 
$x=y\ln(2)$

, this is equivalent to

$\log _{2}(1+2^{y})\approx {\begin{cases}1,&y=0,\\[6pt]{\frac {y}{1-e^{-y}}},&y\neq 0\end{cases}}$

A sharpness parameter 
$k$

 may be included:

$f(x)={\frac {\ln(1+e^{kx})}{k}},\qquad f'(x)={\frac {e^{kx}}{1+e^{kx}}}={\frac {1}{1+e^{-kx}}}$

The derivative of softplus is the logistic function. This in turn can be viewed as a smooth approximation of the derivative of the rectifier, the Heaviside step function.
The multivariable generalization of single-variable softplus is the LogSumExp with the first argument set to zero:

$\operatorname {LSE_{0}} ^{+}(x_{1},\dots ,x_{n}):=\operatorname {LSE} (0,x_{1},\dots ,x_{n})=\ln(1+e^{x_{1}}+\cdots +e^{x_{n}})$

The LogSumExp function is

$\operatorname {LSE} (x_{1},\dots ,x_{n})=\ln(e^{x_{1}}+\cdots +e^{x_{n}})$

and its gradient is the softmax; the softmax with the first argument set to zero is the multivariable generalization of the logistic function. Both LogSumExp and softmax are used in machine learning.

#### ELU

Exponential linear units (2015) smoothly allow negative values. This is an attempt to make the mean activations closer to zero, which speeds up learning. It has been shown that ELUs can obtain higher classification accuracy than ReLUs.

$f(x)={\begin{cases}x&x>0,\\\alpha \left(e^{x}-1\right)&x\leq 0\end{cases}}\qquad f'(x)={\begin{cases}1&x>0,\\\alpha e^{x}&x\leq 0\end{cases}}$

In these formulas, 
$\alpha $

 is a hyperparameter to be tuned with the constraint 
$\alpha \geq 0$

.
Given the same interpretation of 
$\alpha $

, ELU can be viewed as a smoothed version of a shifted ReLU (SReLU), which has the form 
$f(x)=\max(-\alpha ,x)$

.

#### Gaussian-error linear unit (GELU)

GELU (2016) is a smooth approximation to the rectifier:

$f(x)=x\Phi (x)=x\cdot {\frac {1}{2}}\left[1+\operatorname {erf} \left(x/{\sqrt {2}}\right)\right],$
$f'(x)=x\Phi '(x)+\Phi (x)$

where 
$\Phi (x)=P(X\leqslant x)$

 is the cumulative distribution function of the standard normal distribution and 
$\operatorname {erf} (z)$

 is the error function.
This activation function is illustrated in the figure at the start of this article. It has a "bump" with negative derivative to the left of x < 0. It serves as the default activation for many transformer models such as BERT.
The same paper also introduces a few faster approximations for GELU. The first approximation follows from an approximation for 
$\Phi (x)$

:

$f(x)\approx {\frac {1}{2}}x\left(1+\tanh \left[{\sqrt {2/\pi }}\left(x+0.044715x^{3}\right)\right]\right)$

The second, less-precise approximation uses the sigmoid (logistic) function as 
$f(x)\approx x\cdot \operatorname {sigmoid} (1.702x)$

, whose formula resembles SiLU (see below).

#### SiLU

The SiLU (sigmoid linear unit) or swish function is another smooth approximation which uses the sigmoid (logistic) function, first introduced in the 2016 GELU paper:

$f(x)=x\cdot \operatorname {sigmoid} (x),$
$f'(x)=x\cdot \operatorname {sigmoid} '(x)+\operatorname {sigmoid} (x)$

It is cheaper to calculate than GELU. It also has a "bump".

#### Mish

The mish function (2019) can also be used as a smooth approximation of the rectifier. It is defined as

$f(x)=x\tanh {\big (}\operatorname {softplus} (x){\big )},$

where 
$\tanh(x)$

 is the hyperbolic tangent, and 
$\operatorname {softplus} (x)$

 is the softplus function.
Mish was obtained by experimenting with functions similar to Swish (SiLU, see above). It is non-monotonic (has a "bump") like Swish. The main new feature is that it exhibits a "self-regularizing" behavior attributed to a term in its first derivative.

#### Squareplus

Squareplus (2021) is the function

$f(x)={\frac {x+{\sqrt {x^{2}+b}}}{2}}$

where 
$b\geq 0$

 is a hyperparameter that determines the "size" of the curved region near 
$x=0$

. (For example, letting 
$b=0$

 yields ReLU, and letting 
$b=4$

 yields the metallic mean function.)
Squareplus shares many properties with softplus: It is monotonic, strictly positive, approaches 0 as 
$x\to -\infty $

, approaches the identity as 
$x\to +\infty $

, and is 
$C^{\infty }$

 smooth. However, squareplus can be computed using only algebraic functions, making it well-suited for settings where computational resources or instruction sets are limited. Additionally, squareplus requires no special consideration to ensure numerical stability when 
$x$

 is large.

#### DELU

ExtendeD Exponential Linear Unit (DELU, 2023) is an activation function which is smoother within the neighborhood of zero and sharper for bigger values, allowing better allocation of neurons in the learning process for higher performance. Thanks to its unique design, it has been shown that DELU may obtain higher classification accuracy than ReLU and ELU.

$f(x)={\begin{cases}x&x>x_{c},\\(e^{ax}-1)/b&x\leq x_{c}\end{cases}}\qquad f'(x)={\begin{cases}1&x>x_{c},\\(a/b)e^{ax}&x\leq x_{c}\end{cases}}$

In these formulas, 
$a$

, 
$b$

 and 
$x_{c}$

 are hyperparameter values which could be set as default constraints 
$a=1$

, 
$b=2$

 and 
$x_{c}=1.25643$

, as done in the original work.
