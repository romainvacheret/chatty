package communication

import "sync"

type ConnectionManager struct {
	mu sync.RWMutex
	clients []int 
}

func NewConnectionManager() *ConnectionManager {
	return &ConnectionManager{ clients: make([]int, 0)}
}

func (c *ConnectionManager) AddClient(client int) {
	c.mu.Lock()
	c.clients = append(c.clients, client)
	c.mu.Unlock()
}

func (c *ConnectionManager) ListClients() []int {
	c.mu.RLock()
	res := append([]int(nil), c.clients...)
	c.mu.RUnlock()
	return res
}


func (c *ConnectionManager) WriteToClients(message []byte, sender int) {
	for _, client := range c.ListClients() {
		if client != sender {
			Write(client, message)
		}
	}
}
