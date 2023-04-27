---
layout: post
title: "关于Java中的++运算符"
date: 2023-04-24T16:56:44+08:00
categories: java C 副作用
---
有以下java代码:  

```java
int i = 1;
i = i++; // 代码执行完毕后，i的取值为多少
```
## 唔
实际开发中*绝对*_千万_**不**要这样写代码,此类代码**严格禁止**出现在**任何**项目中  
有的话见一个喷一个，喷成翔  
甚至不应该出现在任何书籍上，以免误人子弟  
面试葵花宝典除外
## 想当然的分析:
先给出正确的回答,上面的代码等价于
```java
int i = 1;
```
是的，后面`i=i++;`可以直接去掉(javac不会自动优化掉),毫无作用，或者留在那里恶心人或招bug(比如隐晦地进行了多线程操作)。  
得知真相后，我也很惊讶。还记得谭浩强爷爷教导的,`i++`"就是先操作,再加1"。嗯，我就是这么理解的。  
比如:
```java
int i = 1;
int j = i++;
```
就应该等价于:
```java
int i = 1;
int j = i; // 先赋值
i = i + 1; // 再加1
```
实际运行结果也是如此，即`i == 2`成立

嗯，那么同理:
```java
int i = 1;
i = i++;
```
就应该等价于:
```
int i = 1;
i = i; //先赋值
i = i + 1; //再加1
```
难道...不是么？{:}joy:
## 不是
`javac`编译以下代码:
```java
public class Foo {
	public static void main(String[] args) {
		int i = 1;
		i = i++;
		System.out.println(i); // 打印结果为:1
	}
}
```
执行`javap -v`查看字节码,相关片段及解析如下:
```bytecode
  public static void main(java.lang.String[]);
    descriptor: ([Ljava/lang/String;)V
    flags: (0x0009) ACC_PUBLIC, ACC_STATIC
    Code:
      stack=2, locals=2, args_size=1
         0: iconst_1 // 整数常量1入操作数栈顶
		// 把栈顶整数pop入#1本地变量即i中
		// 本地变量表下标从0开始，函数参数存储在local variable table中
		// 本地变量#0=[Ljava/lang/String,即main函数的参数
         1: istore_1
         2: iload_1 // 把i加载入操作数栈顶, 栈顶元素为i的当前数值1
		 // iinc指令第一个参数为局部点了索引，1即指向局部变量i
		 // 第二个参数为增量,这里为1
		 // iinc直接对局部变量进行操作和改写，无需操作数栈参与
         3: iinc          1, 1 // 执行完毕后i=2,操作数栈顶现在的值依然为数值1
         6: istore_1 // 将栈顶数值(整数1)存入#1本地变量i, 执行完毕后i=1
         7: getstatic     #2                  // Field java/lang/System.out:Ljava/io/PrintStream;
        10: iload_1
        11: invokevirtual #3                  // Method java/io/PrintStream.println:(I)V
```
根据上面的分析，`i=i++`变编译成了`iload_1; iinc 1, 1; istore_1`,即i先存一份副本值到操作数栈顶，然后直接加1到自身，然后再把栈顶元素存储回自身。这个效果...相当于是没有效果。  
不大严谨地大概等价于如下代码:
```java
int i = 1;
int temp = i;
i = i + 1;
i = temp;
```
And that can be reduced to:
```java
int i = 1;
```
嗯...好吧  
接着分析`i=++i`的情况,编译以下代码:
```java
public class Foo1 {
	public static void main(String[] args) {
		int i = 1;
		i = ++i;
		System.out.println(i); // 打印结果为:2, 预期结果
	}
}
```
相关字节码片段及解析如下:
```bytecode
  public static void main(java.lang.String[]);
    descriptor: ([Ljava/lang/String;)V
    flags: (0x0009) ACC_PUBLIC, ACC_STATIC
    Code:
      stack=2, locals=2, args_size=1
         0: iconst_1 // 整数常量1入栈操作数栈
         1: istore_1 // 从操作数栈pop栈顶数值到#1局部变量即i,执行完毕后i=1
         2: iinc          1, 1 // 将局#1部变量i直接增加1,执行完毕后i=2
         5: iload_1 // 将i入操作数栈顶, 执行完毕后stack_top=2, i = 2
         6: istore_1 // 将statck_top pop给局部变量i, 执行完毕后i = 2
         7: getstatic     #2                  // Field java/lang/System.out:Ljava/io/PrintStream;
        10: iload_1
        11: invokevirtual #3                  // Method java/io/PrintStream.println:(I)V
        14: return

```
根据上面的内容可以看到,`i = ++i`对应的字节码为:`iinc 1,1; iload_1;istore_1`,行为和预期语义一致。  
## j=i++和j=++i
以下分别为`j = i++`和`j = ++i`对应的代码片段(省略不必要的部分)
```java {title=代码片段1}
int i = 1;
int j = i++; // j = 1; i = 2
```
```java
int i = 1;
int j = ++i; // j = 2; i = 2
```
其分别对应的字节码为:
```bytecode
         0: iconst_1 // push const integer 1 onto operand stack
         1: istore_1 // pop integer value from operand stack to #1 variable which is i. i = 1
         2: iload_1 // copy value from i onto the top of operand stack. i = 1, stack_top = 1
         3: iinc          1, 1 // add 1 to i directly. i = 2
         6: istore_2 // pop integer value from operand stack to #2 variable which is j. j = 1
```
和
```bytecode
         0: iconst_1
         1: istore_1
         2: iinc          1, 1
         5: iload_1
         6: istore_2
```
将以上自增赋值操作的对应的字节码序列总结到下表：
| 语句 | 字节码序列 |执行结果|
| --- | --- |---|
| i = i++ | `iload_1; iinc 1,1; istore_1` | i==1 |
| j = i++ | `iload_1; iinc 1,1; istore_2` | j == 1 && i == 2 |
| i = ++i | `iinc 1,1; iload_1; istore_1`| i == 2 |
| j = ++i | `iinc 1,1; iload_1; istore_2` | i == 2 && j == 2 |

可以看出`? = ++i`行为和"先加1”(`iinc 1,1`)"再赋值"(`iload_1; istore_?`)的语义一致。  	
而`? = i++`的行为则不是"先赋值,再加1",而是第一步保存原值到一个副本(这里为操作数栈顶)，然后就是"先加1，再(从副本)赋值"  
把`? = i++`编译成`iload_1, istore_?;iincr 1,1`不更符合期望(确切地说是谭爷爷教导的)语义么?

## 为什么会这样呢？为什么非得是这样呢？What is the conventional way?
查文档吧.  
首先,`i++`在java语言规范中规定的语义和行为是什么呢？  
在[jsl-15.14.2](https://docs.oracle.com/javase/specs/jls/se11/html/jls-15.html#jls-15.14.2),有对`i++`
行为的如下关键描述
>The value of the postfix increment expression is the value of the variable before the new value is stored.

即`i++`的返回值为i自增前，i内容改写(嗯，如果有的话)前的值,然后就无更多信息了(当然这个比"先使用再加1”要描述得更清楚规范)  
想想javac会如何看`i=i++`这个语句呢？还是回到jsl文档。  
[jsl-15.7](https://docs.oracle.com/javase/specs/jls/se11/html/jls-15.html#jls-15.7) "Evaluation Order"
有如下描述:  
>The Java programming language **guarantees** that the operands of operators appear to be evaluated in a specific evaluation order, namely, **from left to right**.  
...  
The left-hand operand of a binary operator appears to **be fully evaluated** before any part of the right-hand operand is evaluated.  
...  
The Java programming language guarantees that every operand of an operator (except the conditional operators &&, ||, and ? :) appears to **be fully evaluated** before any part of the operation itself is performed.  
...  
The Java programming language respects the order of evaluation indicated explicitly by parentheses and implicitly by operator precedence.  

上面的措辞**be fully evaluated**，是什么意思呢？  
[jls-15.1](https://docs.oracle.com/javase/specs/jls/se7/html/jls-15.html#jls-15.1) "Evaluation,Denotation, and Result" 有如下对*evaluated*的行为描述:  
> When an expression in a program is evaluated (executed), the result denotes one of three things:
> - A variable (§4.12) (in C, this would be called an lvalue)
> - A value (§4.2, §4.3)
> - Nothing (the expression is said to be void)
> 
> Evaluation of an expression can also produce side effects, because expressions may contain embedded assignments, increment operators, decrement operators, and method invocations.

即evaluation完成后，包含两类动作完成:返回值和副作用(内部状态改变)。  
而对于"be fully evaluated",文档中没有给出明确的正式的严格的定义。  
但根据前面所引用的文档中对"evaluation"的行为描述，加上自然语言常识(也只有这样不大严谨了),应该就可以得出"be fully evalutated"的如下结论：
"be fully evaluated"之后，*返回值完成确定，内部状态改变确定*。
所以，`i=i++`的行为在java的这种规定下就很明确了,`i++`要被`fully evluated`,即在下一个算符运算"="被执行之前，`i++`的副作用状态就必须是发生确定了的，即i自身的状态(值),必须已经由先前的1，变成了计算后的结果2。然后才执行赋值运算，而`i++`运算的返回值为i状态改变前的值。  
即在java中`i=i++`，变量i两次副作用的顺序是确定的，先`i++`的副作用先发生，再发生`i=?`的副作用。  
## 其他
Java出现时是主打内容之一就是安全(比当时的C/C++),在语言层面上不会有未定义的行为出现(大概？)，比如C对于未声明而未初始化的变量或对new出来的内存空间状态就未做规定，而多数编译器的实现就是直接返回一块内存，所以C程序员对于变量必须要初始化或者通过memset将分配到的内存空间reset到确定状态才能放心使用，java的对应方式就是所有的变量都有一个默认的确定状态(绝大多数现代语言也是这么做的)，来保证哪怕出错的行为/状态也是确定的。  
`i++`运算最早是出现在出现C语言的，其语义行为在[C99](https://www.dii.uchile.cl/~daespino/files/Iso_C_1999_definition.pdf)中(最早公开版本C手册我找不到)被定义为:
>The result of the postfix ++ operator is the value of the operand. After the result is
obtained, the value of the operand is incremented.
...
The side effect of updating the stored value of the operand shall occur between
the previous and the next sequence point  

这里不深入解释sequence point,简单类比成这个点后上一步的transaction已经完成，相应的数据已落盘。  
从上面的描述来看，i++还真有点"先使用再加1"的感觉,不管怎么样。在C以后的语言中，如果有`i++`的算符，比如java,其语义也大致和C的相同。  
但这个语义本身并不能描述`i++`的全部行为，虽然觉得上面描述中的*After*好像是表达了`i++`的副作用行为是发生在值返回之后  
但是C标准手册又明确指出,在一个expression中，副作用的先后顺序是'unspecified'的。
在[C99](https://www.dii.uchile.cl/~daespino/files/Iso_C_1999_definition.pdf)的6.5节中的第3点描述如下
>The grouping of operators and operands is indicated by the syntax. Except as specified
later (for the function-call (), &&, ||, ?:, and comma operators), the order of evaluation
of subexpressions and the order in which side effects take place are both unspecified

由于副作用用的存在，计算的先后顺序是很重要的,在命令式语言中副作用也会发生在expression中，所以表达式中各个子表达式计算的先后顺序会影响副作用的状态。而C语言中并没有规定同优先级算符在表达式中的执行顺序，只能保证在同一个表示中，若任何一个变量至多只发生一次副作用，则该表达式的结果是语义层面可以确定的，否则解释权归具体的编译器。所以在C语言中`i=i++`的行为是不确定的，由编译器决定。  
而在java中，则通过明确规定`从左向右`以及'be fully evaluated'就可以很确定地推导出`i=i++`中副作用的先后顺序,以及其他所有expression中的副作用先后顺序。  
另外,在有副作用的语言中，在数学语义上对称的算符,譬如`+`，在这里也是不对称的，不满足交换律。比如无法保证`Op1 + Op2`和`Op2 + Op1`的值是相等的。但是在确定Op1和Op2对任意状态至多只发生一次副作用的情况下可以确定`Op1 + Op2 =:= Op2 + Op1`成立。  
而在C语言层面，由于没有规定同优先级算符的执行顺序，连'Op1+Op2`的值是多少也是在语言层面上无法确认的。
所以在C语言中,
```C
int z = f() + g(); //由于副作用级,算符+的执行顺序是unspecified的，z的值是不确定的
```
应该被改写成如下:
```C
//明确地指定f()和g()的执行顺序，以确定z的值
int x = f();
int y = g();
int z = x + y;
```
而在java中就在语言层面规定"从左向右“地"be fully evaluated",所以"Op1 + Op2"的值是确定的。  
总之在有副作用的语言中，我们无法确定`Op1 + Op2 =:= Op2 + Op1`是否成立。在C语言中，在语言层面上,我们连`Op1 + Op2`的值是多少都无法确定，而java至少从语言层面上保证了我们可以确定`Op1 + Op2`的值。

# 参考连接
1. https://docs.oracle.com/javase/specs/jls/se8/html/jls-15.html
2. https://wiki.sei.cmu.edu/confluence/display/c/EXP30-C.+Do+not+depend+on+the+order+of+evaluation+for+side+effects
3. https://www.dii.uchile.cl/~daespino/files/Iso_C_1999_definition.pdf
4. https://en.wikipedia.org/wiki/Sequence_point
5. https://stackoverflow.com/questions/2028464/logic-differences-in-c-and-java/ 