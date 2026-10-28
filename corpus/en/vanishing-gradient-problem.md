---
title: Vanishing gradient problem
url: https://en.wikipedia.org/wiki/Vanishing_gradient_problem
updated: '2026-08-29T14:41:35Z'
language: en
revision: '1371947961'
license: CC BY-SA 4.0
source: Wikipedia
---

In machine learning, the vanishing gradient problem is the problem of greatly diverging gradient magnitudes between earlier and later layers encountered when training neural networks with backpropagation. In such methods, neural network weights are updated proportional to their partial derivative of the loss function. As the number of forward propagation steps in a network increases, for instance due to greater network depth, the gradients of earlier weights are calculated with increasingly many multiplications. These multiplications shrink the gradient magnitude. Consequently, the gradients of earlier weights will be exponentially smaller than the gradients of later weights. This difference in gradient magnitude might introduce instability in the training process, slow it, or halt it entirely. For instance, consider the hyperbolic tangent activation function. The gradients of this function are in range [0,1]. The product of repeated multiplication with such gradients decreases exponentially. The inverse problem, when weight gradients at earlier layers get exponentially larger, is called the exploding gradient problem.
Backpropagation allowed researchers to train supervised deep artificial neural networks from scratch, initially with little success. Hochreiter's diplom thesis of 1991 formally identified the reason for this failure in the "vanishing gradient problem", which not only affects many-layered feedforward networks, but also recurrent networks. The latter are trained by unfolding them into very deep feedforward networks, where a new layer is created for each time-step of an input sequence processed by the network (the combination of unfolding and backpropagation is termed backpropagation through time).

## Prototypical models

This section is based on the paper On the difficulty of training Recurrent Neural Networks by Pascanu, Mikolov, and Bengio.

### Recurrent network model

A generic recurrent network has hidden states 
$h_{1},h_{2},\dots $

, inputs 
$u_{1},u_{2},\dots $

, and outputs 
$x_{1},x_{2},\dots $

. Let it be parameterized by 
$\theta $

, so that the system evolves as

$(h_{t},x_{t})=F(h_{t-1},u_{t},\theta )$

Often, the output 
$x_{t}$

 is a function of 
$h_{t}$

, as some 
$x_{t}=G(h_{t})$

. The vanishing gradient problem already presents itself clearly when 
$x_{t}=h_{t}$

, so we simplify our notation to the special case with:

$x_{t}=F(x_{t-1},u_{t},\theta )$

Now, take its differential:

${\begin{aligned}dx_{t}&=\nabla _{\theta }F(x_{t-1},u_{t},\theta )d\theta +\nabla _{x}F(x_{t-1},u_{t},\theta )dx_{t-1}\\&=\nabla _{\theta }F(x_{t-1},u_{t},\theta )d\theta +\nabla _{x}F(x_{t-1},u_{t},\theta )\left[\nabla _{\theta }F(x_{t-2},u_{t-1},\theta )d\theta +\nabla _{x}F(x_{t-2},u_{t-1},\theta )dx_{t-2}\right]\\&\;\;\vdots \\&=\left[\nabla _{\theta }F(x_{t-1},u_{t},\theta )+\nabla _{x}F(x_{t-1},u_{t},\theta )\nabla _{\theta }F(x_{t-2},u_{t-1},\theta )+\cdots \right]d\theta \end{aligned}}$

Training the network requires us to define a loss function to be minimized. Let it be 
$L(x_{T},u_{1},\dots ,u_{T})$

, then minimizing it by gradient descent gives

$\Delta \theta =-\eta \cdot \left[\nabla _{x}L(x_{T})\left(\nabla _{\theta }F(x_{t-1},u_{t},\theta )+\nabla _{x}F(x_{t-1},u_{t},\theta )\nabla _{\theta }F(x_{t-2},u_{t-1},\theta )+\cdots \right)\right]^{T}$

where 
$\eta $

 is the learning rate.
The vanishing/exploding gradient problem appears because there are repeated multiplications, of the form
$\nabla _{x}F(x_{t-1},u_{t},\theta )\nabla _{x}F(x_{t-2},u_{t-1},\theta )\nabla _{x}F(x_{t-3},u_{t-2},\theta )\cdots $

#### Example: recurrent network with sigmoid activation

For a concrete example, consider a typical recurrent network defined by

$x_{t}=F(x_{t-1},u_{t},\theta )=W_{\text{rec}}\sigma (x_{t-1})+W_{\text{in}}u_{t}+b$

where 
$\theta =(W_{\text{rec}},W_{\text{in}})$

 is the network parameter, 
$\sigma $

 is the sigmoid activation function, applied to each vector coordinate separately, and 
$b$

 is the bias vector.
Then, 
$\nabla _{x}F(x_{t-1},u_{t},\theta )=W_{\text{rec}}\operatorname {diag} (\sigma '(x_{t-1}))$

, and so

${\begin{aligned}&\nabla _{x}F(x_{t-1},u_{t},\theta )\nabla _{x}F(x_{t-2},u_{t-1},\theta )\cdots \nabla _{x}F(x_{t-k},u_{t-k+1},\theta )\\&=W_{\text{rec}}\operatorname {diag} (\sigma '(x_{t-1}))W_{\text{rec}}\operatorname {diag} (\sigma '(x_{t-2}))\cdots W_{\text{rec}}\operatorname {diag} (\sigma '(x_{t-k}))\end{aligned}}$

Since 
$\left|\sigma '\right|\leq 1$

, the operator norm of the above multiplication is bounded above by 
$\left\|W_{\text{rec}}\right\|^{k}$

. So if the spectral radius of 
$W_{\text{rec}}$

 is 
$\gamma <1$

, then at large 
$k$

, the above multiplication has operator norm bounded above by 
$\gamma ^{k}\to 0$

. This is the prototypical vanishing gradient problem.
The effect of a vanishing gradient is that the network cannot learn long-range effects. Recall Equation (loss differential):
$\nabla _{\theta }L=\nabla _{x}L(x_{T},u_{1},\dots ,u_{T})\left[\nabla _{\theta }F(x_{t-1},u_{t},\theta )+\nabla _{x}F(x_{t-1},u_{t},\theta )\nabla _{\theta }F(x_{t-2},u_{t-1},\theta )+\cdots \right]$

The components of 
$\nabla _{\theta }F(x,u,\theta )$

 are just components of 
$\sigma (x)$

 and 
$u$

, so if 
$u_{t},u_{t-1},\dots $

 are bounded, then 
$\left\|\nabla _{\theta }F(x_{t-k-1},u_{t-k},\theta )\right\|$

 is also bounded by some 
$M>0$

, and so the terms in 
$\nabla _{\theta }L$

 decay as 
$M\gamma ^{k}$

. This means that, effectively, 
$\nabla _{\theta }L$

 is affected only by the first 
$O(\gamma ^{-1})$

 terms in the sum.
If 
$\gamma \geq 1$

, the above analysis does not quite work. For the prototypical exploding gradient problem, the next model is clearer.

### Dynamical systems model

Following (Doya, 1993), consider this one-neuron recurrent network with sigmoid activation:

$x_{t+1}=(1-\varepsilon )x_{t}+\varepsilon \sigma (wx_{t}+b)+\varepsilon w'u_{t}$

At the small 
$\varepsilon $

 limit, the dynamics of the network becomes

${\frac {dx}{dt}}=-x(t)+\sigma (wx(t)+b)+w'u(t)$

Consider first the autonomous case, with 
$u=0$

. Set 
$w=5.0$

, and vary 
$b$

 in 
$[-3,-2]$

. As 
$b$

 decreases, the system has 1 stable point, then has 2 stable points and 1 unstable point, and finally has 1 stable point again. Explicitly, the stable points are 
$(x,b)=\left(x,\ln \left({\frac {x}{1-x}}\right)-5x\right)$

.
Now consider 
${\frac {\Delta x(T)}{\Delta x(0)}}$

 and 
${\frac {\Delta x(T)}{\Delta b}}$

, where 
$T$

 is large enough that the system has settled into one of the stable points.
If 
$(x(0),b)$

 puts the system very close to an unstable point, then a tiny variation in 
$x(0)$

 or 
$b$

 would make 
$x(T)$

 move from one stable point to the other. This makes 
${\frac {\Delta x(T)}{\Delta x(0)}}$

 and 
${\frac {\Delta x(T)}{\Delta b}}$

 both very large, a case of the exploding gradient.
If 
$(x(0),b)$

 puts the system far from an unstable point, then a small variation in 
$x(0)$

 would have no effect on 
$x(T)$

, making 
${\frac {\Delta x(T)}{\Delta x(0)}}=0$

, a case of the vanishing gradient.
Note that in this case, 
${\frac {\Delta x(T)}{\Delta b}}\approx {\frac {\partial x(T)}{\partial b}}=\left({\frac {1}{x(T)(1-x(T))}}-5\right)^{-1}$

 neither decays to zero nor blows up to infinity. Indeed, it's the only well-behaved gradient, which explains why early researches focused on learning or designing recurrent networks systems that could perform long-ranged computations (such as outputting the first input it sees at the very end of an episode) by shaping its stable attractors.
For the general case, the intuition still holds ( Figures 3, 4, and 5).

### Geometric model

Continue using the above one-neuron network, fixing 
$w=5,x(0)=0.5,u(t)=0$

, and consider a loss function defined by 
$L(x(T))=(0.855-x(T))^{2}$

. This produces a rather pathological loss landscape: as 
$b$

 approach 
$-2.5$

 from above, the loss approaches zero, but as soon as 
$b$

 crosses 
$-2.5$

, the attractor basin changes, and loss jumps to 0.50.
Consequently, attempting to train 
$b$

 by gradient descent would "hit a wall in the loss landscape", and cause exploding gradient. A slightly more complex situation is plotted in, Figures 6.

## Solutions

To overcome this problem, several methods were proposed.

### RNN

For recurrent neural networks, the long short-term memory (LSTM) network was designed to solve the problem (Hochreiter & Schmidhuber, 1997).
For the exploding gradient problem, (Pascanu et al, 2012) recommended gradient clipping, meaning dividing the gradient vector 
$g$

 by 
$\left\|g\right\|/g_{\text{max}}$

 if 
$\left\|g\right\|>g_{\text{max}}$

. This restricts the gradient vectors within a ball of radius 
$g_{\text{max}}$

.

### Batch normalization

Batch normalization is a standard method for solving both the exploding and the vanishing gradient problems.

### Multi-level hierarchy

In multi-level hierarchy of networks (Schmidhuber, 1992), pre-trained one level at a time through unsupervised learning, fine-tuned through backpropagation. Here each level learns a compressed representation of the observations that is fed to the next level.

### Deep belief network

Similar ideas have been used in feed-forward neural networks for unsupervised pre-training to structure a neural network, making it first learn generally useful feature detectors. Then the network is trained further by supervised backpropagation to classify labeled data. The deep belief network model by Hinton et al. (2006) involves learning the distribution of a high-level representation using successive layers of binary or real-valued latent variables. It uses a restricted Boltzmann machine to model each new layer of higher level features. Each new layer guarantees an increase on the lower-bound of the log likelihood of the data, thus improving the model, if trained properly. Once sufficiently many layers have been learned the deep architecture may be used as a generative model by reproducing the data when sampling down the model (an "ancestral pass") from the top level feature activations. Hinton reports that his models are effective feature extractors over high-dimensional, structured data.

### Faster hardware

Hardware advances have meant that from 1991 to 2015, computer power (especially as delivered by GPUs) has increased around a million-fold, making standard backpropagation feasible for networks several layers deeper than when the vanishing gradient problem was recognized. Schmidhuber notes that this "is basically what is winning many of the image recognition competitions now", but that it "does not really overcome the problem in a fundamental way" since the original models tackling the vanishing gradient problem by Hinton and others were trained in a Xeon processor, not GPUs.

### Residual connection

Residual connections, or skip connections, refers to the architectural motif of 
$x\mapsto f(x)+x$

, where 
$f$

 is an arbitrary neural network module. This gives the gradient of 
$\nabla f+I$

, where the identity matrix do not suffer from the vanishing or exploding gradient. During backpropagation, part of the gradient flows through the residual connections.
Concretely, let the neural network (without residual connections) be 
$f_{n}\circ f_{n-1}\circ \cdots \circ f_{1}$

, then with residual connections, the gradient of output with respect to the activations at layer 
$l$

 is 
$I+\nabla f_{l+1}+\nabla f_{l+2}\nabla f_{l+1}+\cdots $

. The gradient thus does not vanish in arbitrarily deep networks.
Feedforward networks with residual connections can be regarded as an ensemble of relatively shallow nets. In this perspective, they resolve the vanishing gradient problem by being equivalent to ensembles of many shallow networks, for which there is no vanishing gradient problem.

### Other activation functions

Rectifiers such as ReLU suffer less from the vanishing gradient problem, because they only saturate in one direction.

### Weight initialization

Weight initialization is another approach that has been proposed to reduce the vanishing gradient problem in deep networks.
Kumar suggested that the distribution of initial weights should vary according to activation function used and proposed to initialize the weights in networks with the logistic activation function using a Gaussian distribution with a zero mean and a standard deviation of 
$3.6/{\sqrt {N}}$

, where 
$N$

 is the number of neurons in a layer.
In 2022, Yilmaz and Poli performed a theoretical analysis on how gradients are affected by the mean of the initial weights in deep neural networks using the logistic activation function and found that gradients do not vanish if the mean of the initial weights is set according to the formula: 
$\max(-1,-8/N)$

. This simple strategy allows networks with 10 or 15 hidden layers to be trained very efficiently and effectively using the standard backpropagation.

### Other

Behnke relied only on the sign of the gradient (Rprop) when training his Neural Abstraction Pyramid to solve problems like image reconstruction and face localization.
Neural networks can also be optimized by using a universal search algorithm on the space of neural network's weights, e.g., random guess or more systematically genetic algorithm. This approach is not based on gradient and avoids the vanishing gradient problem.
