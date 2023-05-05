---
layout: post
title: "substitution models for function application"
date: 2023-05-05T10:33:19+08:00
categories:
---

假设有段如下类javascript语言的代码:

```js
function foo(x, y) {
    // 假设该该语言中，三目运算支持短路
    // 并且假设 关键字'return'和三目运算符是原语操作
    return x == 0? 1: y;
}

// 假设这个语言中对0进行除法运算会抛出异常'ArithmeticException'
foo(0 , 1/0); // 请问这行代码的执行结果
```

在[sicp javascript版本][1]的1.1.5节中有介绍function application evaluation的两种替换顺序, 'applicative order' 和'normal order'，有其中如下描述：
>... the interpreter first evaluates the function and argument expressions and then applies the resulting function to the resulting arguments. This is not the only way to perform evaluation. An alternative evaluation model would not evaluate the arguments until their values were needed. Instead it would first substitute argument expressions for parameters until it obtained an expression involving only operators and primitive functions, and would then perform the evaluation

大致来说就是,normal order先直接把参数带入函数体进行归约操作, 在归约的过程中，需要参数的值的话，再计算参数的值。  
normal order的归约过程大致如下:

```none
foo(0, 1/0)
=>
return 0 == 0? 1: 1 / 0
=>
return 1
```

即若该语言使用的是,normal order的方式来对函数调用进行evaluation的话，foo(0, 1/0)的返回值为1  
而applicative order则是先计算参数的值(这里我们假设参数的计算顺序是确定的，从左向右依次计算)。  
归约过程大致如下

```none
foo(0, 1/0)
=>
0->0 // evaluate 1th paramater literal value 0 as value 0
=>
1/0 // evaluate 2nd paramter expression 1/0. Opps, 'AritheticExcecption' raised. The evaluation of 'foo(0, 1/0)' terminates abruptly with 'AritheticException'
```

即若该语言使用的是applicative order的顺序来对函数进行evaluation的话，对于上面的代码示例，则会抛出'AritheticException'的异常  

Java语言是applictive order的，其他的类C语言也大多是applictive order的。  
下面的Java代码:

```java
public class Foo {
    public static void main(String[] args) {
        foo(0, 1/0);
    }
    private static int foo(int x, int y) {
        return x==0 ? 1: y;
    }
}
```

执行时会抛出异常信息:'Exception in thread "main" java.lang.ArithmeticException: / by zero'  

让我感到意外的是scheme居然也是applicative order的,以下scheme代码的均是在'Chez Scheme Version 9.5'这个版本的解释器下进行的验证。  
首先在scheme, 0作为除数运算是会抛出异常的。例如

```scheme
(/ 1 0)
```

在执行时会抛出'Exception in /: undefined for 0'的异常  
而开头示例代码对应的scheme代码则是如下:

``` scheme
(define (foo x y)
  (if (= x 0)
      1
      y))

(foo 0 (/ 0 1))
```

在执行时也会抛出'Exception in /: undefined for 0'的异常  

而haskell则是normal order的，以下hs代码均在ghci vesion 8.6.5中进行验证。
首先,haskell中整除运算div，0作为除数是会抛出异常的。例如

```haskell
div 1 0
```

在执行时会抛出'Exception: divide by zero'的错误信息(hs中`1/0`则会返回'infinity'这个常量,js中`1/0`返回常量'Infinity')  
在开头示例代码对应的haskell代码及执行信息如下:

```haskell
foo x y = if x == 0 then 1 else y
foo 0 $ div 1 0 -- 执行结果为1,即在归约过程中未被使用的表达`div 1 0`最终不会被计算
```

作为对比,继续执行刚才定义的函数`foo`

```haskell
foo 1 $ div 1 0 -- 抛出错误信息 'Exception: divide by zero'
```

所有通过该示例明显可以看出haskell是normal order的。  
那javascript呢？是normal order还是applictive order的呢?  
其实开头的示例代码就是javascript,但是在js中`1/0`的值为常量`Infinity`，并不会抛出异常，从而改变代码执行流程。整除运算`1//0`的结果为1,也不会抛出异常改变代码的execution flow。  
所以修改代码如下：

 ```js
 function foo(x, y) {
    return x === 0 ? 1: y;
 }

 // x===0是成立的,但是applicative order使得在参数计算时就发生异常，改变了执行流
 // 从而使得foo函数体中的三目运算得不到执行
 foo(0, (()=>{throw Error("Opps"))()}) 
 ```

 执行的结果为抛出异常'Uncaught Error: Opps', 而不是返回1, 并且javascript中问号三目运算符是会短路的，即在js repl中执行执行执行如下语句值:

 ```js
 0 === 0 ? 1 : (()=>{throw Error('Opps')})() // 返回值为1
 0 === 1 ? 1 : (()=>{throw Error('Opps')})() // 抛出异常'Uncaught Error: Opps'
 ```

从上面的代码示例中，可以看出javascript的函数计算是applicative order的。

另外请注意，上面的js代码中`(()=>{throw Error('Opps')})()`是函数调用,而不是函数定义  
而在上面的haskell代码中`div 1 0`,同样也是函数调用，而不是函数定义

参考书籍及链接:  
[1]: "Structure and Interpretation of Computer Programs (javascript Edtion)", MIT press, 2022  
[2]: https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/6515/sicp.zip/full-text/book/book-Z-H-10.html#%_sec_1.1.5
