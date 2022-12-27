package main

import (
	"crypto/tls"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"reflect"
	"runtime"
	"time"
)

const directory = "GUI/";
const  operatingSystem = runtime.GOOS;

func main() {
	var portObj = argument_parser();
	println(portObj[0]);
	file_server := http.FileServer(http.Dir(directory));
	http.Handle("/", file_server);
	http.HandleFunc("/post", post);
	server := http.Server{
		Addr:              portObj[0] + ":" + portObj[1],
		Handler:           nil,
		TLSConfig:         &tls.Config{},
		ReadTimeout:       30 * time.Second,
		ReadHeaderTimeout: 0,
		WriteTimeout:      30 * time.Second,
		IdleTimeout:       0,
		MaxHeaderBytes:    1 << 20,
		TLSNextProto:      map[string]func(*http.Server, *tls.Conn, http.Handler){},
	};
	log.Printf("Serving %s on HTTP port: %s:%s\n", directory, portObj[0], portObj[1]);
	log.Fatal(server.ListenAndServeTLS("cert.pem","key.pem"));
}

func argument_parser() []string{
	var returnObj []string;
	h := flag.String("h", "", "Input IP address");
	p := flag.String("p", "8000", "Input port number");
	flag.Parse();
	fmt.Println("host: ", *h);
	fmt.Println("port: ", *p);
	returnObj = []string{*h, *p};
	return returnObj;
}

func loadJson(inputPath string) interface{} {
	byteArray, _ := ioutil.ReadFile(inputPath);
	var jsonObj interface{};
	_ = json.Unmarshal(byteArray, &jsonObj);
	return jsonObj;
}

func writeJson(jsonObj interface{}, outputPath string) {
	file, _ := os.Create(outputPath);
	defer file.Close();
	_ = json.NewEncoder(file).Encode(jsonObj);
}

func getJsonValue(jsonObj interface{}, key []string) string {
	println("serch key: ", key);
	var returnObj string;
	var tempObj interface{} = jsonObj;
	for i:=0; i<len(key); i++ {
		tempObj = tempObj.(map[string]interface{})[key[i]];
	};
	returnObj = tempObj.(string);
	return returnObj;
}

func post(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		fmt.Fprint(w, "Method not supported.\n");
		return;
	};
	switch r.FormValue("type"){
		case "update":
			fmt.Println("Update requested");
			post_update(w, r);
		case "done":
			fmt.Println("Done requested");
			post_done(w, r);
		case "delete":
			fmt.Println("Delete requested");
			post_delete(w, r);
		case "shutdown":
			w.WriteHeader(http.StatusCreated);
			fmt.Println("Shutdown requested");
			os.Exit(0);
		default:
			w.WriteHeader(http.StatusBadRequest);
			fmt.Fprint(w, "Unknown request type");
			return;
	}
}

func post_update(w http.ResponseWriter, r *http.Request) {
	var class_list = "False";
	var update_list = "";
	var pythonCommand = "python";
	if operatingSystem == "darwin" {
		pythonCommand = "python3";
	}
	switch r.FormValue("key") {
		case "c":
			class_list = "True";
		case "dA":
			class_list = "False";
			update_list = "all";
		case "cdA":
			class_list = "True";
			update_list = "all";
		default:
			class_list = "True";
			update_list = r.FormValue("key");
	}
	if len(update_list) != 0 {
		err := exec.Command(pythonCommand, "checker.py", "-c", class_list, "-u", update_list).Run();
		fmt.Println(err);
	} else {
		err := exec.Command(pythonCommand, "checker.py", "-c", class_list).Run();
		fmt.Println(err);
	}
	data_json := loadJson("./GUI/data.json");
	send_data := map[string] interface{}{
		"classList": data_json.(map[string]interface{})["classList"],
		"classDetails": data_json.(map[string]interface{})["classDetails"],
	}
	bytes, _ := json.Marshal(send_data);

	w.WriteHeader(http.StatusCreated);
	w.Header().Set("Content-Type", "application/json");
	w.Write([]byte(string(bytes)));
}

func post_done(w http.ResponseWriter, r *http.Request) {
	data_json := loadJson("./GUI/data.json");
	done := data_json.(map[string]interface{})["done"];
	key := r.FormValue("key");
	dumpItem := []string{};

	for i := 0; i < len(done.([]interface{})); i++ {
		dumpItem = append(dumpItem, done.([]interface{})[i].(string))
	}

	dumpItem = append(dumpItem, key);
	data_json.(map[string]interface{})["done"] = dumpItem;

	writeJson(data_json, "./GUI/data.json")

	fmt.Println(dumpItem);
	fmt.Println(reflect.TypeOf(dumpItem));

	w.WriteHeader(http.StatusCreated);
	w.Header().Set("Content-Type", "application/json");
	w.Write([]byte(string(key)));
}

func post_delete(w http.ResponseWriter, r *http.Request) {
	data_json := loadJson("./GUI/data.json");
	done := data_json.(map[string]interface{})["invisible"];
	key := r.FormValue("key");
	dumpItem := []string{};

	for i := 0; i < len(done.([]interface{})); i++ {
		dumpItem = append(dumpItem, done.([]interface{})[i].(string))
	}

	dumpItem = append(dumpItem, key);
	data_json.(map[string]interface{})["invisible"] = dumpItem;

	writeJson(data_json, "./GUI/data.json")

	fmt.Println(dumpItem);
	fmt.Println(reflect.TypeOf(dumpItem));

	w.WriteHeader(http.StatusCreated);
	w.Header().Set("Content-Type", "application/json");
	w.Write([]byte(string(key)));
}