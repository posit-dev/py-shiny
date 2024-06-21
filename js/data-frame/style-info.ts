// This file is oddly close to `useCellEditMap.tsx`

import { enableMapSet } from "immer";
import { useCallback, useEffect } from "react";
import { Updater, useImmer } from "use-immer";

enableMapSet();

export type CellStyle = { [key: string]: string | null };

export type StyleInfoData = {
  // locname: LocNames;
  locname: "data";
  locnum: number;
  grpname: string | null;
  // colname: string | null;
  rownum: number;
  colnum: number;
  styles: CellStyle;
};
export type StyleInfo = StyleInfoData;
// export type Styles = StyleInfo[];

export type InitStyleInfoData = Omit<StyleInfoData, "styles"> & {
  styles: string;
};
export type InitStyleInfo = InitStyleInfoData;

type LocNames = StyleInfo["locname"];

export type StyleInfoMap = Map<string, StyleInfo>;

export const makeStyleInfoMapKey = ({
  locname,
  rowIndex,
  columnIndex,
}: {
  locname: LocNames;
  rowIndex: number;
  columnIndex: number;
}) => {
  return `[${locname}, ${rowIndex}, ${columnIndex}]`;
};

export type SetStyleInfoMap = Updater<StyleInfoMap>;
export type SetStyleInfo = (style: StyleInfo | InitStyleInfo) => void;
/**
 *
 * @param initStyleInfos Array of initial style information containing whose `styles` are represented as strings
 * @returns {{styleInfoMap: StyleInfoMap, setStyleInfo: SetStyleInfo}} where `styleInfoMap` is a map of style information and `setStyleInfo` is a function to update the map
 */
export const useStyleInfoMap = (
  initStyleInfos: StyleInfo[]
): {
  styleInfoMap: StyleInfoMap;
  setStyleInfo: SetStyleInfo;
} => {
  const [styleInfoMap, setStyleInfoMap] = useImmer<StyleInfoMap>(
    new Map<string, StyleInfo>()
  );
  const setStyleInfo: SetStyleInfo = useCallback(
    (styleInfo: StyleInfo | InitStyleInfo) => {
      const styleInfoVal = toStyleInfo(styleInfo);
      const { locname, rownum: rowIndex, colnum: columnIndex } = styleInfoVal;

      setStyleInfoMap((draft) => {
        const key = makeStyleInfoMapKey({ locname, rowIndex, columnIndex });
        draft.set(key, styleInfoVal);
      });
    },
    [setStyleInfoMap]
  );

  // Init all style infos
  useEffect(() => {
    initStyleInfos.forEach(setStyleInfo);
  }, [initStyleInfos, setStyleInfo]);

  return {
    styleInfoMap,
    setStyleInfo,
  } as const;
};

export const styleInfoMapHasKey = (
  x: StyleInfoMap,
  locname: LocNames,
  rowIndex: number,
  columnIndex: number
) => {
  return x.has(makeStyleInfoMapKey({ locname, rowIndex, columnIndex }));
};
export const getCellStyle = (
  x: StyleInfoMap,
  locname: LocNames,
  rowIndex: number,
  columnIndex: number
): CellStyle | undefined => {
  const key = makeStyleInfoMapKey({ locname, rowIndex, columnIndex });
  return x.get(key)?.styles;
};

function toStyleInfo(styleInfo: StyleInfo | InitStyleInfo): StyleInfo {
  if (typeof styleInfo.styles === "string") {
    return {
      ...styleInfo,
      styles: cssStringToObj(styleInfo.styles),
    };
  }
  return styleInfo as StyleInfo;
}

// TODO-barret look for CSS parser from browser
// Naive method to convert css string to object
// Adapted from https://stackoverflow.com/a/68853314/591574
function cssStringToObj(strVal: string): { [key: string]: string } {
  const jsonInner = strVal
    .replace(/;\s*$/, "")
    .replace(/;/g, '", "')
    .replace(/: /g, '": "');
  const cssJsonStr = `{"${jsonInner}"}`;

  const obj: { [key: string]: string } = JSON.parse(cssJsonStr);

  const keyValues = Object.keys(obj).map((key) => {
    const camelCased = key.replace(/-[a-z]/g, (g) => g[1].toUpperCase());
    return { [camelCased]: obj[key] };
  });
  return Object.assign({}, ...keyValues);
}
