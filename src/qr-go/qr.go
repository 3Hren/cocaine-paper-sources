package main

import (
	"net/http"

	"code.google.com/p/rsc/qr"
	"github.com/ugorji/go/codec"

	"github.com/cocaine/cocaine-framework-go/cocaine"
)

//msgpack specific
var (
	mh codec.MsgpackHandle
	h  = &mh
)

var (
	OkHeaders    cocaine.Headers = cocaine.Headers{[2]string{"Content-type", "image/png"}}
	ErrorHeaders cocaine.Headers = cocaine.Headers{[2]string{"Content-type", "text/plain"}}

	storage *cocaine.Service
)

const (
	cacheNamepspace = "qr-code"
	cacheTag        = "qr-tag"
)

func qenerate(text string) (png []byte, err error) {
	res := <-storage.Call("read", cacheNamepspace, text)
	if res.Err() == nil {
		err = res.Extract(&png)
		return
	}

	c, err := qr.Encode(text, qr.L)
	if err != nil {
		return
	}
	png = c.PNG()

	<-storage.Call("write", cacheNamepspace, text, string(png), []string{cacheTag})
	return
}

func on_generate(request *cocaine.Request, response *cocaine.Response) {
	defer response.Close()
	inc := <-request.Read()
	var task struct {
		Text string
		Size int
	}

	err := codec.NewDecoderBytes(inc, h).Decode(&task)
	if err != nil {
		response.ErrorMsg(-100, err.Error())
		return
	}

	png, err := qenerate(task.Text)
	if err != nil {
		response.ErrorMsg(-200, err.Error())
		return
	}

	response.Write(png)
}

func on_http_generate(request *cocaine.Request, response *cocaine.Response) {
	defer response.Close()
	r, err := cocaine.UnpackProxyRequest(<-request.Read())
	if err != nil {
		response.ErrorMsg(-200, err.Error())
		return
	}

	message := r.FormValue("message")
	if len(message) == 0 {
		response.Write(cocaine.WriteHead(http.StatusBadRequest, ErrorHeaders))
		response.Write("Missing argument `message`")
		return
	}

	png, err := qenerate(message)
	if err != nil {
		response.Write(cocaine.WriteHead(http.StatusInternalServerError, ErrorHeaders))
		response.Write("Unable to generate QR")
		return
	}

	response.Write(cocaine.WriteHead(http.StatusOK, OkHeaders))
	response.Write(png)
}

func main() {
	binds := map[string]cocaine.EventHandler{
		"generate":      on_generate,
		"generate-http": on_http_generate,
	}

	Worker, err := cocaine.NewWorker()
	if err != nil {
		panic(err)
	}

	storage, err = cocaine.NewService("storage")
	if err != nil {
		panic(err)
	}

	Worker.Loop(binds)
}
