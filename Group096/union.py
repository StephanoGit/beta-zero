class UnionFind:
    def __init__(self) -> None:
        self.parent = {}
        self.rank = {}
        self.groups = {}
        self.ignored = []

    def join(self, x, y) -> bool:
        rep_x = self.find(x)
        rep_y = self.find(y)

        if rep_x == rep_y:
            return False
        if self.rank[rep_x] < self.rank[rep_y]:
            self.parent[rep_x] = rep_y

            self.groups[rep_y].extend(self.groups[rep_x])
            del self.groups[rep_x]
        elif self.rank[rep_x] > self.rank[rep_y]:
            self.parent[rep_y] = rep_x

            self.groups[rep_x].extend(self.groups[rep_y])
            del self.groups[rep_y]
        else:
            self.parent[rep_x] = rep_y
            self.rank[rep_y] += 1

            self.groups[rep_y].extend(self.groups[rep_x])
            del self.groups[rep_x]

        return True

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            if x in self.ignored:
                self.groups[x] = []
            else:
                self.groups[x] = [x]

        px = self.parent[x]
        if x == px:
            return x

        gx = self.parent[px]
        if gx == px:
            return px

        self.parent[x] = gx

        return self.find(gx)

    def connected(self, x, y) -> bool:
        return self.find(x) == self.find(y)

    def set_ignored_elements(self, ignore):
        self.ignored = ignore

    def get_groups(self) -> dict:
        return self.groups
