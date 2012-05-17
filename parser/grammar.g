parser TinyEnglish:
  ignore:          "\\W+"
  token noun:      "(Jack|spam|ship)"
  token verb:      "(sank|threw)"
  token article:   "(a|an|the)"
  token adjective: "(blue|red|green)"

  rule sentence:       noun_phrase verb noun_phrase
  rule noun_phrase:    [article] adjective* noun
