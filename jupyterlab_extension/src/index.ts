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
import { tag } from './tag';

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
  activate: async (
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

    await injectShinyDependencies();
  }
};

async function injectShinyDependencies() {
  document.head.append(
    tag('link', { rel: 'stylesheet', href: '/shiny/shared/shiny.min.css' }),
    tag('link', {
      href: '/shiny/shared/bootstrap/bootstrap.min.css',
      rel: 'stylesheet'
    }),
    tag('link', {
      href: '/shiny/shared/ionrangeslider/css/ion.rangeSlider.css',
      rel: 'stylesheet'
    })
  );

  // Dynamically inserted <script> tags aren't guaranteed to load in order, so we need
  // to serialize them using each one's load event.
  const scripts = [
    '/shiny/shared/jquery/jquery-3.6.0.js',
    '/shiny/shared/shiny.js',
    '/shiny/shared/bootstrap/bootstrap.bundle.min.js',
    '/shiny/shared/ionrangeslider/js/ion.rangeSlider.min.js'
  ];
  for (const script of scripts) {
    await loadScript(script);
  }
}

async function loadScript(src: string): Promise<void> {
  let scriptEl = tag('script', { type: 'text/javascript', src });
  document.head.appendChild(scriptEl);
  return new Promise((resolve, reject) => {
    scriptEl.onload = e => {
      console.log(`Loaded ${src}`);
      resolve();
    };
    scriptEl.onerror = e => {
      reject(new Error(`Failed to load JS script: ${src}`));
    };
  });
}

export default plugin;

class HtmltoolsRenderer extends Widget implements IRenderMime.IRenderer {
  constructor(options: IRenderMime.IRendererOptions) {
    super();
    this.addClass('htmltools-output');
  }

  async renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    const shinyBind = tag('shiny-bind');
    const content = JSON.parse(model.data[MIME_TYPE] as any) || {};
    const renderFunc =
      window.Shiny.renderContentAsync || window.Shiny.renderContent;

    await renderFunc(shinyBind, content, 'replace');

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
    try {
      socket.send(event.data);
    } catch (e) {
      console.error('Failed to send: ', e);
      // TODO: Should we really dispose without any more information? But I didn't
      // see any open/closed state property in the docs, and onClose clearly isn't
      // getting called.
      dispose();
    }
  }
  superclient.addEventListener('send', onSend);

  socket.onclose = function onclose(event: CloseEvent) {
    console.log(
      "Socket closed. Code: '" + event.code + "'. Reason: " + event.reason
    );
    dispose();
  };

  function dispose() {
    socket.onmessage = null;
    superclient.removeEventListener('send', onSend);
  }
}
