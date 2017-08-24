class edge(set):
   def __init__(self,a0,a1,b,c):
      if a0 < a1:
         self.a0 = a0
         self.a1 = a1
      else:
         self.a0 = a1
         self.a1 = a0
      self.b = b
      self.c = c

      x = int(b); x = x+x if x >= 0 else -1-x-x
      y = int(c); y = y+y if y >= 0 else -1-y-y
      self.ft = ( x*x + x + y if x >= y else x + y*y )

   def query_points(self,a0,a1):
      if a0 > a1: reverse_rqrd,a0,a1 = True,a1,a0
      else: reverse_rqrd = False
      points = []
      for e in self:
         if a0 < e[0] < a1: points.append(e[0])
         if a0 < e[1] < a1: points.append(e[1])
      points.sort(reverse=reverse_rqrd)
      return points

   def __eq__(self,other): return self.a0 < other.a1 and self.a1 > other.a0 and self.b == other.b and self.c == other.c

   def __hash__(self): return self.ft


class edges(dict):
   def add(self,a0,a1,b,c,quad):
      k = edge(a0,a1,b,c)
      e = self.pop(k,k)
      if e is not k:
         while True:
            i = self.pop(k,e)
            if i is not e:
               for s in i: s[2].change_edge(i,e)
               e |= i
            else: break
         e.a0 = k.a0
         e.a1 = k.a1
      self[e] = e
      for s in e:
         if s[0] < a0 < s[1] or s[1] < a0 < s[0] or s[0] < a1 < s[1] or s[1] < a1 < s[0]: s[2].update()
         if s[0] < e.a0: e.a0 = s[0]
         if s[1] < e.a0: e.a0 = s[1]
         if s[0] > e.a1: e.a1 = s[0]
         if s[1] > e.a1: e.a1 = s[1]
      e.add( (a0,a1,quad) )
      return e

   def sub(self,a0,a1,e,quad):
      e.remove( (a0,a1,quad) )
      if e:
         e.a0,e.a1 = e.a1,e.a0
         for s in e:
            if s[0] < a0 < s[1] or s[1] < a0 < s[0] or s[0] < a1 < s[1] or s[1] < a1 < s[0]: s[2].update()
            if s[0] < e.a0: e.a0 = s[0]
            if s[1] < e.a0: e.a0 = s[1]
            if s[0] > e.a1: e.a1 = s[0]
            if s[1] > e.a1: e.a1 = s[1]
      else: self.pop(e)
