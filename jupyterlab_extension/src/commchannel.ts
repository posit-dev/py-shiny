import { DocumentWidget } from '@jupyterlab/docregistry';

function debug(...args: any[]) {
  console.log(...args);
}

export function createNotebookComm(notebookWidget: DocumentWidget) {
  const kernel = notebookWidget.context?.sessionContext?.session?.kernel;

  // // I don't know how to get the ConsolePanel type, so duck type. (I tried adding
  // // @jupyterlab/console to the dependencies, but then jlnp no longer worked.)
  // const consoleWidget = app.shell.currentWidget;
  // kernel = (consoleWidget as any)?.sessionContext?.session?.kernel;

  if (!kernel) {
    throw new Error(
      'Shiny could not establish a connection to the kernel. Please open a notebook first!'
    );
  }

  let comm = kernel.createComm('shiny');
  return new KernelSocket(comm);
}

export function createConsoleComm(consoleWidget: any) {
  // I don't know how to get the ConsolePanel type, so duck type. (I tried adding
  // @jupyterlab/console to the dependencies, but then jlnp no longer worked.)
  const kernel = (consoleWidget as any)?.sessionContext?.session?.kernel;

  if (!kernel) {
    return null;
  }

  let comm = kernel.createComm('shiny');
  return new KernelSocket(comm);
}

// CommToWS is a wrapper around a Jupyter Comm that implements the WebSocket interface
export class KernelSocket {
  comm: any;
  onmessage: any;
  onopen: any;
  onclose: any;
  onerror: any;
  readyState: number = WebSocket.CONNECTING;
  allowReconnect: boolean = false;

  constructor(comm: any) {
    this.comm = comm;
    this.comm.onMsg = this._onmessage.bind(this);
    this.comm.onClose = this._onclose.bind(this);
  }

  _onmessage(msg: any) {
    if (this.readyState === WebSocket.CONNECTING) {
      console.log('_onopen');
      this.readyState = WebSocket.OPEN;
      if (this.onopen) {
        this.onopen();
      }
    }

    debug(this.comm.commId, '_onmessage: ', msg.content.data);
    if (this.onmessage) {
      // TODO: Remove extra serialization
      this.onmessage({ data: JSON.stringify(msg.content.data) });
    }
  }
  _onclose(msg: any) {
    debug(this.comm.commId, '_onclose: ', msg);
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      // TODO: I'm sure this msg unpacking is wrong
      this.onclose(msg.content.data);
    }
  }
  send(msg: any) {
    debug(this.comm.commId, 'send: ', JSON.parse(msg));
    // TODO: Remove extra deserialization
    this.comm.send(JSON.parse(msg));
  }
  close() {
    this.readyState = WebSocket.CLOSING;
    this.comm.close();
  }
}
