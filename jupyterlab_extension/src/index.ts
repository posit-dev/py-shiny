import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { PageConfig } from '@jupyterlab/coreutils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { IRenderMime, IRenderMimeRegistry } from '@jupyterlab/rendermime';

import { Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';

import { registerElement } from './shiny-bind-element';
import { SuperclientWebSocket as SuperclientSocket } from './superclient';
import { KernelSocket } from './commchannel';

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
      widget.context?.sessionContext?.kernelChanged.connect(() => {
        console.log(
          'Kernel is now: ',
          widget.context?.sessionContext?.session?.kernel?.id
        );
        widget.context?.sessionContext?.session?.kernel?.registerCommTarget(
          'shiny-kernel',
          (comm, msg) => {
            console.log('shiny-kernel comm channel established');
            // TODO: Might need to force the inputs to be sent to the comm right now
            const ks = new KernelSocket(comm);
            connect(window.Shiny.superclient, ks);
            ks.send(
              JSON.stringify({
                method: 'init',
                data: window.Shiny.shinyapp.$inputValues
              })
            );
          }
        );
      });
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
    window.Shiny.superclient = new SuperclientSocket();
    window.Shiny.createSocket = () => {
      setTimeout(() => {
        window.Shiny.superclient.setToOpen();
      }, 0);
      return window.Shiny.superclient;
    };

    injectShinyDependencies();
  }
};

function injectShinyDependencies() {
  document.head.append(
    tag('link', { rel: 'stylesheet', href: '/shiny/shared/shiny.min.css' }),
    tag('script', { src: '/shiny/shared/jquery/jquery-3.6.0.js' }),
    tag('script', { src: '/shiny/shared/shiny.js' }),
    tag('link', {
      href: '/shiny/shared/bootstrap/bootstrap.min.css',
      rel: 'stylesheet'
    }),
    tag('script', { src: '/shiny/shared/bootstrap/bootstrap.bundle.min.js' }),
    tag('script', {
      src: '/shiny/shared/ionrangeslider/js/ion.rangeSlider.min.js'
    }),
    tag('link', {
      href: '/shiny/shared/ionrangeslider/css/ion.rangeSlider.css',
      rel: 'stylesheet'
    })
  );
}

function tag(tagname: string, attrs: Record<string, string>) {
  const el = document.createElement(tagname);
  Object.entries(attrs).forEach(([k, v]) => {
    el.setAttribute(k, v);
  });
  return el;
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

export function connect(superclient: SuperclientSocket, socket: KernelSocket) {
  socket.onmessage = (event: MessageEvent) => {
    superclient.dispatchEvent(
      new MessageEvent('message', { data: event.data })
    );
  };

  function onSend(event: MessageEvent) {
    socket.send(event.data);
  }
  superclient.addEventListener('send', onSend);

  socket.onclose = function onclose(event: CloseEvent) {
    console.log(
      "Socket closed. Code: '" + event.code + "'. Reason: " + event.reason
    );
    socket.onmessage = null;
    superclient.removeEventListener('send', onSend);
  };
}
