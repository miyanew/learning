# デザインパターンを学ぼう

- [結城浩の公式 > デザインパターンを学ぼう。](https://www.hyuki.com/dp/)

## デザインパターンとは

- 丸暗記するものではない（昔から変わらず）
- OOPに適用される（関数型プログラミングには適用されない、ほかのパターンを見出すべき）
- リファクタリングのゴールのモデルを示すらしい
- GoFの語る2009年時点での実用性。
  - Core:
    - 11.Composite
    - 10.Strategy
    - 19.State
    - 22.Command
    - 01.Iterator
    - 21.Proxy
    - 03.Template Method
    - 15.Facade
  - Creational:
    - 04.Factory（Factory Methodを一般化）
    - 06.Prototype
    - 07.Builder
    - xx.Dependency Injection
  - Peripheral:
    - 08.Abstract Factory
    - 13.Visitor
    - 12.Decorator
    - 16.Mediator
    - xx.Type Object
    - xx.Null Object
    - xx.Extension Object
  - Other:
    - 23.Interpreter
    - 20.Flyweight
  - Delete:
    - 02.Adapter
    - 05.Singleton
    - 09.Bridge
    - 14.Chain of Responsiblity
    - 17.Memento
    - 18.Observer

- [Design Patterns 15 Years Later: An Interview with Erich Gamma, Richard Helm, and Ralph Johnson \| Design Patterns 15 Years Later: An Interview with Erich Gamma, Richard Helm, and Ralph Johnson \| InformIT](https://www.informit.com/articles/article.aspx?p=1404056)
  - 分類の変化 ※1994年時の分類: 生成、構造、ふるまい。  Peripheral:あまり使わない の意
  - 削除6, 変更1, 追加4
