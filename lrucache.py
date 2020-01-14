import time

# memcached
# redis：LRU算法，但是还有一些主动淘汰策略，线程轮询一下tail指针，过期的就干一干。

# 代表一个value的封装，它是字典的value部分，是链表的node
class Entry:
    def __init__(self, key, value, ttl):
        self.key = key
        self.value = value
        self.prev = self.next = None
        if ttl == -1:
            self.expire_at = None
        else:
            self.expire_at = int(time.time()) + ttl

    def is_expired(self):
        now = int(time.time())
        if self.expire_at is None:
            return False
        return now > self.expire_at

class LRUCache:
    def __init__(self, max_size):
        self.max_size = max_size
        self.dict = {}
        self.head = self.tail = Entry(None, None, -1)

    def _insert_entry(self, entry):
        if self.head == self.tail:
            self.tail = entry
        entry.next = self.head.next
        entry.prev = self.head
        if self.head.next is not None:
            self.head.next.prev = entry
        self.head.next = entry

    def _delete_entry(self, entry):
        entry.prev.next = entry.next
        if entry.next is not None:
            entry.next.prev = entry.prev
        if entry == self.tail:
            self.tail = entry.prev

    def _shrink(self):
        # 控制容量
        if len(self.dict) > self.max_size:
            if self.head == self.tail:
                return
            entry = self.tail
            self._delete_entry(entry)
            del self.dict[entry.key]
    
    def set(self, key, value, ttl=-1):
        # 如果key已经存在，把它先从lru cache里面完全清掉
        if key in self.dict:
            # 删字典
            entry = self.dict[key]
            del self.dict[key]
            # 删链表
            self._delete_entry(entry)

        # 插链表
        entry = Entry(key,value,ttl)
        self.dict[key] = entry  # 先存到字典
        self._insert_entry(entry)

        # 控制容量
        self._shrink()
    
    def get(self, key):
        if key in self.dict:
            entry = self.dict[key]
            if not entry.is_expired():
                self._delete_entry(entry)
                self._insert_entry(entry)
                return entry.value
        return None

    def delete(self, key):
        if key in self.dict:
            entry = self.dict[key]
            del self.dict[key]
            self._delete_entry(entry)
    

if __name__ == '__main__':
    cache = LRUCache(max_size=3)
    for i in range(5):  # 0,12,3,4
        cache.set(str(i), i, i)

    for i in range(5):
        #time.sleep(1.1)
        print('~~~~~', cache.get(str(i)))
    
    cache.set('2', 1)
    print('-----', cache.get('3'))
    
    cur = cache.head
    while cur.next is not None:     # head -> 3 -> 2 -> 4 -> None
        print(cur.next.key)
        cur = cur.next
    
