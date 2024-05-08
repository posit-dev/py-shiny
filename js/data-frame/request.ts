// type JobId = string;
// type UploadUrl = string;
// type UploadInitValue = { jobId: JobId; uploadUrl: UploadUrl };
// type UploadEndValue = never;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type ResponseValue = any;

export type OnSuccessRequest = (value: ResponseValue) => void;
export type OnErrorRequest = (err: string) => void;

// Websocket messages are normally one-way--i.e. the client passes a
// message to the server but there is no way for the server to provide
// a response to that specific message. makeRequest provides a way to
// do asynchronous RPC over websocket. Each request has a method name
// and arguments, plus optionally one or more binary blobs can be
// included as well. The request is tagged with a unique number that
// the server will use to label the corresponding response.
//
// @param method A string that tells the server what logic to run.
// @param args An array of objects that should also be passed to the
//   server in JSON-ified form.
// @param onSuccess A function that will be called back if the server
//   responds with success. If the server provides a value in the
//   response, the function will be called with it as the only argument.
// @param onError A function that will be called back if the server
//   responds with error, or if the request fails for any other reason.
//   The parameter to onError will be a string describing the error.
// @param blobs Optionally, an array of Blob, ArrayBuffer, or string
//   objects that will be made available to the server as part of the
//   request. Strings will be encoded using UTF-8.
export function makeRequest(
  method: string,
  args: unknown[],
  onSuccess: OnSuccessRequest,
  onError: OnErrorRequest,
  blobs: Array<ArrayBuffer | Blob | string> | undefined
) {
  window.Shiny.shinyapp!.makeRequest(method, args, onSuccess, onError, blobs);
}

export function makeRequestPromise({
  method,
  args,
  blobs,
}: {
  method: string;
  args: unknown[];
  blobs?: Array<ArrayBuffer | Blob | string> | undefined;
}) {
  return new Promise((resolve, reject) => {
    makeRequest(
      method,
      args,
      (value: ResponseValue) => {
        resolve(value);
      },
      (err: string) => {
        reject(err);
      },
      blobs
    );
  });
}
