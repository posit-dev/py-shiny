// This file is oddly close to `useCellEditMap.tsx`

import { enableMapSet } from "immer";
import { useCallback, useEffect } from "react";
import { Updater, useImmer } from "use-immer";

enableMapSet();

export type CellStyle = { [key: string]: string | null };

type StyleInfoBody = {
  location: "body";
  rows: number[] | null;
  cols: number[] | null;
  style?: CellStyle;
  class?: string;
};
export type StyleInfo = StyleInfoBody;
// export type Styles = StyleInfo[];

type StyleInfoStoredBody = {
  location: "body";
  rowIndex: number;
  columnIndex: number;
  style?: CellStyle;
  class?: string;
};
export type StyleInfoStored = StyleInfoStoredBody;

type StyleLocation = StyleInfo["location"];

export type StyleInfoMap = Map<string, StyleInfoStored>;

export const makeStyleInfoMapKey = ({
  location,
  rowIndex,
  columnIndex,
}: {
  location: StyleLocation;
  rowIndex: number;
  columnIndex: number;
}) => {
  return `[${location}, ${rowIndex}, ${columnIndex}]`;
};

export type SetStyleInfoStoredMap = Updater<StyleInfoMap>;
export type SetStyleInfo = (style: StyleInfo) => void;
export type SetStyleInfos = (style: StyleInfo[]) => void;
export type ResetStyleInfos = () => void;
/**
 *
 * @param initStyleInfos Array of initial style information
 * @returns {{styleInfoMap: StyleInfoMap, setStyleInfo: SetStyleInfo}} where `styleInfoMap` is a map of style information and `setStyleInfo` is a function to update the map
 */
export const useStyleInfoMap = ({
  initStyleInfos,
  nrow,
  ncol,
}: {
  initStyleInfos: StyleInfo[];
  nrow: number;
  ncol: number;
}): {
  styleInfoMap: StyleInfoMap;
  setStyleInfo: SetStyleInfo;
  setStyleInfos: SetStyleInfos;
  resetStyleInfos: ResetStyleInfos;
} => {
  const [styleInfoMap, setStyleInfoMap] = useImmer<StyleInfoMap>(
    new Map<string, StyleInfoStored>()
  );
  const setStyleInfo: SetStyleInfo = useCallback(
    (styleInfo: StyleInfo) => {
      const { location, rows, cols } = styleInfo;

      setStyleInfoMap((draft) => {
        const rowArr = rows ?? Array.from({ length: nrow }, (_, i) => i);
        const colArr = cols ?? Array.from({ length: ncol }, (_, j) => j);
        for (const rowIndex of rowArr) {
          for (const columnIndex of colArr) {
            const key = makeStyleInfoMapKey({
              location,
              rowIndex,
              columnIndex,
            });
            draft.set(key, {
              location: styleInfo.location,
              rowIndex,
              columnIndex,
              style: styleInfo.style,
              class: styleInfo.class,
            });
          }
        }
      });
    },
    [ncol, nrow, setStyleInfoMap]
  );

  const resetStyleInfos = useCallback(() => {
    setStyleInfoMap((draft) => {
      draft.clear();
    });
  }, [setStyleInfoMap]);

  const setStyleInfos = useCallback(
    (styleInfos: StyleInfo[]) => {
      for (const styleInfo of styleInfos) {
        setStyleInfo(styleInfo);
      }
    },
    [setStyleInfo]
  );

  // Init all style infos
  useEffect(() => {
    setStyleInfos(initStyleInfos);
  }, [initStyleInfos, setStyleInfos]);

  return {
    styleInfoMap,
    setStyleInfo,
    setStyleInfos,
    resetStyleInfos,
  } as const;
};

export const styleInfoMapHasKey = (
  x: StyleInfoMap,
  location: StyleLocation,
  rowIndex: number,
  columnIndex: number
) => {
  return x.has(makeStyleInfoMapKey({ location, rowIndex, columnIndex }));
};
export const getCellStyle = (
  x: StyleInfoMap,
  location: StyleLocation,
  rowIndex: number,
  columnIndex: number
): CellStyle | undefined => {
  const key = makeStyleInfoMapKey({ location, rowIndex, columnIndex });
  return x.get(key)?.style;
};

// Use a DOM element to convert CSS string to object
const cssStringToObjDomElement = document.createElement("cssStringToObj");
function cssStringToObj(strVal: string): { [key: string]: string } {
  cssStringToObjDomElement.style.cssText = strVal;
  const style = cssStringToObjDomElement.style;

  const ret: { [key: string]: string } = {};
  Array.from(style).forEach((key) => {
    ret[key] = style.getPropertyValue(key);
  });

  return ret;
}
