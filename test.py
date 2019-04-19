class Rapper():
    def __init__(self, theme):
        self.theme = theme

    def printStuff(self):
        print(self.theme + "testfs")

if __name__ == "__main__":
  theme = input()
  structureModel = Structure("MCKCorpus.txt")


  # model = [
  #   (FIRSTPART, SECONDPART, FREQ),
  #   (FIRSTPART, SECONDPART, FREQ),
  #   (FIRSTPART, SECONDPART, FREQ),
  #   (FIRSTPART, SECONDPART, FREQ),
  #   ...
  # ]
  # (VB, NN, 50%)
  # NN, ADJ 20%

  rapper = Rapper(theme, structureModel.model)
  rapper.rap()
