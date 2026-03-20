package tui

import (
	"bytes"
	"chatty/internal/communication"
	"chatty/internal/logger"
	"strings"

	"github.com/jroimartin/gocui"
)

const (
	viewDisplay = "display"
	viewInput   = "input"
)


type ClientTui struct {
	sender *communication.ClientSender
	gui *gocui.Gui
}

func NewClientTui(sender *communication.ClientSender) (*ClientTui, error) {
	gui, err := gocui.NewGui(gocui.OutputNormal)
	if err != nil { return nil, err }

	res := &ClientTui{ sender: sender, gui: gui }
	res.gui.SetManagerFunc(setLayout)

	if err := res.setKeybindings(gui); err != nil { return nil, err }

	return res, nil
}

func (c *ClientTui) RunMainLoop() error {
	defer c.gui.Close()

	go c.sender.Listen(func(buff []byte) {
		c.gui.Update(func(g *gocui.Gui) error {
			if view, err := g.View(viewDisplay); err != nil {
				return err
			} else {
				_, err := view.Write(append(bytes.TrimSpace(buff), byte('\n')))
				return err
			}
		})
	})
	
	if err := c.gui.MainLoop(); err == gocui.ErrQuit { 
		return  nil
	} else {
		return err
	}
}

func setLayout(g *gocui.Gui) error {
	maxX, maxY := g.Size()

	if displayView, err := g.SetView(viewDisplay, 0, 0, maxX - 1, maxY - 4); err != nil {
		if err != gocui.ErrUnknownView {
			return err
		}
		displayView.Title = "Messages"
		displayView.Wrap = true
		displayView.Autoscroll = true
	}

	if inputView, err := g.SetView(viewInput, 0, maxY - 3, maxX - 1, maxY - 1); err != nil {
		if err != gocui.ErrUnknownView {
			return err
		}
		inputView.Title = "Input"
		inputView.Editable = true
		inputView.Editor = gocui.DefaultEditor
		inputView.Wrap = true

		if _, err := g.SetCurrentView(viewInput); err != nil {
			return err
		}
	}

	return nil
}

func (c *ClientTui) setKeybindings(g *gocui.Gui) error {
	if err := g.SetKeybinding("", gocui.KeyCtrlC, gocui.ModNone, quit); err != nil {
		return err
	}

	if err := g.SetKeybinding(viewInput, gocui.KeyEnter, gocui.ModNone, c.submitMessage); err != nil {
		return err
	}

	return nil
}

func quit(g *gocui.Gui, v *gocui.View) error {
	return gocui.ErrQuit
}

func (c *ClientTui) submitMessage(g *gocui.Gui, v *gocui.View) error {
	input := strings.TrimSpace(v.Buffer())

	if input != "" {
		if err := c.sender.Send(input); err != nil { return err }
		if view, err := g.View(viewDisplay); err != nil {
			return err 
		} else {
			view.Write(append([]byte(input), byte('\n')))
		}
	}

	v.Clear()
	v.SetCursor(0, 0)
	v.SetOrigin(0, 0)

	return nil
}
