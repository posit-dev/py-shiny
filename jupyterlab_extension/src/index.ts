import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { PageConfig } from '@jupyterlab/coreutils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { DocumentWidget } from '@jupyterlab/docregistry';
import { IRenderMime, IRenderMimeRegistry } from '@jupyterlab/rendermime';

import { Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';

import { registerElement } from './shiny-bind-element';

// This has the side-effect of registering the custom element
registerElement();

declare global {
  interface Window {
    Shiny: any;
  }
}

const MIME_TYPE = 'application/vnd.posit.htmltools+json';

/**
 * Initialization data for the jupyterlab-shiny extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-shiny:plugin',
  description:
    'A JupyterLab extension for running interactive Shiny applications directly within notebooks.',
  autoStart: true,
  requires: [INotebookTracker, IRenderMimeRegistry],
  activate: (
    app: JupyterFrontEnd,
    notebookTracker: INotebookTracker,
    renderMimeRegistry: IRenderMimeRegistry
  ) => {
    console.log('JupyterLab extension jupyterlab-shiny is activated!');
    const baseUrl = PageConfig.getBaseUrl();
    console.log('baseUrl: ', baseUrl);

    notebookTracker.widgetAdded.connect((sender, widget) => {
      console.log('Notebook widget added: ', widget);
    });

    renderMimeRegistry.addFactory(
      {
        safe: false,
        mimeTypes: [MIME_TYPE],
        createRenderer: function (
          options: IRenderMime.IRendererOptions
        ): IRenderMime.IRenderer {
          return new HtmltoolsRenderer(options);
        }
      },
      0
    );

    window.Shiny = window.Shiny || {};
    window.Shiny.createSocket = () => {
      let kernel = null;
      const notebookWidget = app.shell.currentWidget;
      if (notebookWidget instanceof DocumentWidget) {
        kernel = notebookWidget.context?.sessionContext?.session?.kernel;
      }

      // I don't know how to get the ConsolePanel type, so duck type. (I tried adding
      // @jupyterlab/console to the dependencies, but then jlnp no longer worked.)
      const consoleWidget = app.shell.currentWidget;
      kernel = (consoleWidget as any)?.sessionContext?.session?.kernel;

      if (!kernel) {
        throw new Error(
          'Shiny could not establish a connection to the kernel. Please open a notebook first!'
        );
      }

      let comm = kernel.createComm('shiny');
      return new CommToWS(comm);
    };
  }
};

// CommToWS is a wrapper around a Jupyter Comm that implements the WebSocket interface
class CommToWS {
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

    this.comm.open({});
  }

  _onmessage(msg: any) {
    if (this.readyState === WebSocket.CONNECTING) {
      console.log('_onopen');
      this.readyState = WebSocket.OPEN;
      if (this.onopen) {
        this.onopen();
      }
    }

    console.log('_onmessage: ', msg);
    if (this.onmessage) {
      // TODO: Remove extra serialization
      this.onmessage({ data: JSON.stringify(msg.content.data) });
    }
  }
  _onclose(msg: any) {
    console.log('_onclose: ', msg);
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      // TODO: I'm sure this msg unpacking is wrong
      this.onclose(msg.content.data);
    }
  }
  send(msg: any) {
    console.log('Shiny client is sending: ', msg);
    // TODO: Remove extra deserialization
    this.comm.send(JSON.parse(msg));
  }
  close() {
    this.readyState = WebSocket.CLOSING;
    this.comm.close();
  }
}

export default plugin;

class HtmltoolsRenderer extends Widget implements IRenderMime.IRenderer {
  constructor(options: IRenderMime.IRendererOptions) {
    super();
    this.addClass('htmltools-output');
  }

  async renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    const shinyBind = document.createElement('shiny-bind');
    shinyBind.innerHTML = JSON.parse(model.data[MIME_TYPE] as any)?.html;
    this.node.replaceChildren(shinyBind);
  }

  onAfterAttach(msg: Message): void {}
}
