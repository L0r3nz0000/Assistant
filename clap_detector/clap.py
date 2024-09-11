from .TapTester import TapTester

class MyTapTester(TapTester):
  def double_clap_callback(self, callback, args=()):
    self.callback_2 = callback
    self.args_2 = args
  
  def single_clap_callback(self, callback, args=()):
    self.callback_1 = callback
    self.args_1 = args
