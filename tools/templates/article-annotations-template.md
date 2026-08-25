annotations:
  - id: example-link
    type: link
    skin: box-1
    title: "链接解析标题"
    text: "这里写链接背景、出处说明、为什么这个链接值得读。"
    url: "https://example.com"
    link_label: "原始出处"
  - id: example-image
    type: image
    skin: box-8
    title: "图片补充"
    image: /assets/img/example.jpg
    image_alt: "图片说明"
    caption: "图片下方短说明。"
    text: "这里写图片和正文的关系。"

正文里这样引用：

{% raw %}{% include annotation-ref.html id="example-link" text="需要评注的文字" %}{% endraw %}
